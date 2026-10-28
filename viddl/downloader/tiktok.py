"""TikTok: видео (пытаемся без водяного знака)."""
from __future__ import annotations

import logging

import yt_dlp

from viddl.downloader.base import (
    BaseDownloader, DownloadError, DownloadResult, VideoInfo,
)

log = logging.getLogger(__name__)


class TikTokDownloader(BaseDownloader):
    name = "tiktok"
    domains = ("tiktok.com", "vm.tiktok.com", "vt.tiktok.com")

    def download(self, url: str) -> DownloadResult:
        # yt-dlp для TikTok предпочитает версии без watermark при наличии.
        opts = {
            "format": "best",
            "outtmpl": str(self.options.output_dir /
                           "tiktok_%(uploader)s_%(title).100s_%(id)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
            "retries": self.options.retries,
            "continuedl": True,
        }
        if self.options.cookies_file:
            opts["cookiefile"] = str(self.options.cookies_file)
        if self.options.proxy:
            opts["proxy"] = self.options.proxy
        if self.options.skip_existing:
            opts["download_archive"] = str(self.options.output_dir / ".archive_tiktok.txt")

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                fp = None
                if info_dict.get("requested_downloads"):
                    fp = info_dict["requested_downloads"][0].get("filepath")
                if not fp:
                    raise DownloadError("TikTok: не удалось определить путь файла")
                info = VideoInfo(
                    id=str(info_dict.get("id", "")),
                    title=info_dict.get("title") or "tiktok_video",
                    author=info_dict.get("uploader") or "",
                    duration=info_dict.get("duration"),
                    description=(info_dict.get("description") or "")[:2000],
                    upload_date=info_dict.get("upload_date"),
                    url=url,
                    platform=self.name,
                )
                from pathlib import Path
                path = Path(fp)
                self._save_metadata(info, path)
                return DownloadResult(url=url, success=True, filepath=path, info=info)
        except yt_dlp.utils.DownloadError as exc:
            raise DownloadError(f"TikTok: {exc}") from exc
        except Exception as exc:  # noqa: BLE001
            raise DownloadError(f"TikTok: {exc}") from exc