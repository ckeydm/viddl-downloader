"""Twitch: клипы (не стримы в реальном времени)."""
from __future__ import annotations

import logging
from pathlib import Path

import yt_dlp

from viddl.downloader.base import (
    BaseDownloader, DownloadError, DownloadResult, VideoInfo,
)

log = logging.getLogger(__name__)


class TwitchDownloader(BaseDownloader):
    name = "twitch"
    domains = ("twitch.tv", "clips.twitch.tv")

    def download(self, url: str) -> DownloadResult:
        if "/videos/" in url or url.rstrip("/").count("/") < 4:
            # это не клип — предупредим
            log.warning("Twitch: поддерживаются клипы; VOD/стримы могут не скачаться")
        opts = {
            "format": "best",
            "outtmpl": str(self.options.output_dir /
                           "twitch_%(uploader)s_%(title).80s_%(id)s.%(ext)s"),
            "quiet": True, "no_warnings": True,
            "retries": self.options.retries,
        }
        if self.options.cookies_file:
            opts["cookiefile"] = str(self.options.cookies_file)
        if self.options.proxy:
            opts["proxy"] = self.options.proxy
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                fp = (info_dict.get("requested_downloads") or [{}])[0].get("filepath")
                if not fp:
                    raise DownloadError("Twitch: клип недоступен")
                info = VideoInfo(
                    id=str(info_dict.get("id", "")),
                    title=info_dict.get("title") or "twitch_clip",
                    author=info_dict.get("uploader") or "",
                    duration=info_dict.get("duration"),
                    description=(info_dict.get("description") or "")[:2000],
                    upload_date=info_dict.get("upload_date"),
                    url=url,
                    platform=self.name,
                )
                path = Path(fp)
                self._save_metadata(info, path)
                return DownloadResult(url=url, success=True, filepath=path, info=info)
        except yt_dlp.utils.DownloadError as exc:
            raise DownloadError(f"Twitch: {exc}") from exc