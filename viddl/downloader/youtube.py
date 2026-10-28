"""YouTube: видео, Shorts, плейлисты."""
from __future__ import annotations

import logging
from typing import Any

import yt_dlp

from viddl.downloader.base import (
    BaseDownloader, DownloadError, DownloadOptions, DownloadResult, VideoInfo,
)

log = logging.getLogger(__name__)


class YouTubeDownloader(BaseDownloader):
    name = "youtube"
    domains = ("youtube.com", "youtu.be", "youtube-nocookie.com")

    def download(self, url: str) -> DownloadResult:
        opts = self._ydl_opts()
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                # Плейлист -> entries
                entries = info_dict.get("entries") or [info_dict]
                results = []
                for entry in entries:
                    if entry is None:
                        continue
                    filepath = self._resolve_filepath(entry)
                    if filepath is None:
                        continue
                    info = self._to_info(entry, url)
                    self._save_metadata(info, filepath)
                    results.append(DownloadResult(url=url, success=True,
                                                  filepath=filepath, info=info))
                if not results:
                    raise DownloadError("Не удалось получить ни одного файла")
                # Для плейлиста возвращаем первый успешный как агрегат
                return results[0]
        except yt_dlp.utils.DownloadError as exc:
            raise DownloadError(self._humanize_error(exc)) from exc
        except Exception as exc:  # noqa: BLE001
            raise DownloadError(f"YouTube: непредвиденная ошибка: {exc}") from exc

    # ---------- helpers ----------

    def _ydl_opts(self) -> dict[str, Any]:
        fmt = self._format_selector()
        opts: dict[str, Any] = {
            "format": fmt,
            "outtmpl": str(self.options.output_dir /
                           "%(extractor)s_%(uploader)s_%(title).100s_%(id)s.%(ext)s"),
            "restrictfilenames": False,
            "noplaylist": False,
            "retries": self.options.retries,
            "fragment_retries": self.options.retries,
            "continuedl": True,
            "quiet": True,
            "no_warnings": True,
            "ignoreerrors": False,
        }
        if self.options.cookies_file:
            opts["cookiefile"] = str(self.options.cookies_file)
        if self.options.proxy:
            opts["proxy"] = self.options.proxy
        if self.options.audio_only or self.options.quality == "audio":
            opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            })
        if self.options.skip_existing:
            opts["download_archive"] = str(self.options.output_dir / ".archive.txt")
        return opts

    def _format_selector(self) -> str:
        q = self.options.quality.lower()
        if q in ("audio", "audioonly"):
            return "bestaudio/best"
        if q == "best":
            return "bestvideo*+bestaudio/best"
        if q.endswith("p") and q[:-1].isdigit():
            h = q[:-1]
            return (f"bestvideo[height<={h}]+bestaudio/"
                    f"best[height<={h}]/best")
        return "bestvideo*+bestaudio/best"

    @staticmethod
    def _resolve_filepath(entry: dict[str, Any]) -> Any:
        from pathlib import Path
        if entry.get("requested_downloads"):
            fp = entry["requested_downloads"][0].get("filepath")
            if fp:
                return Path(fp)
        return None

    def _to_info(self, e: dict[str, Any], url: str) -> VideoInfo:
        return VideoInfo(
            id=str(e.get("id", "")),
            title=e.get("title") or "untitled",
            author=e.get("uploader") or e.get("channel") or "",
            duration=e.get("duration"),
            description=(e.get("description") or "")[:2000],
            upload_date=e.get("upload_date"),
            url=url,
            platform=self.name,
        )

    @staticmethod
    def _humanize_error(exc: Exception) -> str:
        msg = str(exc)
        mapping = {
            "Private video": "Видео приватное.",
            "This video is unavailable": "Видео недоступно (удалено/гео-блок).",
            "Sign in to confirm your age": "Требуется подтверждение возраста — укажите cookies.",
            "This video is only available for": "Гео-ограничение.",
            "Captcha": "Платформа требует капчу.",
        }
        for key, human in mapping.items():
            if key in msg:
                return f"YouTube: {human}"
        return f"YouTube: {msg}"