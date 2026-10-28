"""Vimeo."""
from __future__ import annotations

import logging
from pathlib import Path

import yt_dlp

from viddl.downloader.base import (
    BaseDownloader, DownloadError, DownloadResult, VideoInfo,
)

log = logging.getLogger(__name__)


class VimeoDownloader(BaseDownloader):
    name = "vimeo"
    domains = ("vimeo.com", "player.vimeo.com")

    def download(self, url: str) -> DownloadResult:
        q = self.options.quality
        fmt = "best"
        if q not in ("best", "audio") and q.endswith("p"):
            fmt = f"best[height<={q[:-1]}]/best"
        opts = {
            "format": fmt,
            "outtmpl": str(self.options.output_dir /
                           "vimeo_%(uploader)s_%(title).80s_%(id)s.%(ext)s"),
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
                    raise DownloadError("Vimeo: файл не создан")
                info = VideoInfo(
                    id=str(info_dict.get("id", "")),
                    title=info_dict.get("title") or "vimeo_video",
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
            raise DownloadError(f"Vimeo: {exc}") from exc