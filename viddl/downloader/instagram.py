"""Instagram: Reels, посты с видео, IGTV. Fallback на instaloader."""
from __future__ import annotations

import logging
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp

from viddl.downloader.base import (
    BaseDownloader, DownloadError, DownloadResult, VideoInfo,
)

log = logging.getLogger(__name__)


class InstagramDownloader(BaseDownloader):
    name = "instagram"
    domains = ("instagram.com", "instagr.am")

    def download(self, url: str) -> DownloadResult:
        try:
            return self._via_ytdlp(url)
        except DownloadError as first_err:
            log.warning("yt-dlp не справился с Instagram (%s), пробуем instaloader", first_err)
            return self._via_instaloader(url)

    # ---------- yt-dlp ----------

    def _via_ytdlp(self, url: str) -> DownloadResult:
        opts = {
            "format": "best",
            "outtmpl": str(self.options.output_dir /
                           "instagram_%(uploader)s_%(title).80s_%(id)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
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
                    raise DownloadError("Instagram: пустой результат")
                info = VideoInfo(
                    id=str(info_dict.get("id", "")),
                    title=info_dict.get("title") or "instagram_post",
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
            raise DownloadError(f"Instagram/yt-dlp: {exc}") from exc

    # ---------- instaloader fallback ----------

    def _via_instaloader(self, url: str) -> DownloadResult:
        try:
            import instaloader
        except ImportError as exc:
            raise DownloadError(
                "Instagram: требуется instaloader. Установите: pip install instaloader"
            ) from exc

        loader = instaloader.Instaloader(
            dirname_pattern=str(self.options.output_dir / "{target}"),
            filename_pattern="{shortcode}",
            download_video_thumbnails=False,
            save_metadata=False,
            post_metadata_txt_pattern="",
            quiet=True,
        )
        if self.options.cookies_file:
            try:
                # instaloader использует cookies-файл в формате Mozilla
                loader.load_session_from_file(
                    username=self._guess_username(self.options.cookies_file),
                    filename=str(self.options.cookies_file),
                )
            except Exception as exc:  # noqa: BLE001
                log.warning("Не удалось загрузить сессию Instaloader: %s", exc)

        path = urlparse(url).path.strip("/")
        parts = path.split("/")
        # /reel/<shortcode>/ | /p/<shortcode>/
        if len(parts) < 2:
            raise DownloadError("Instagram: не удалось разобрать URL")
        shortcode = parts[1]
        try:
            post = instaloader.Post.from_shortcode(loader.context, shortcode)
            if not post.is_video:
                raise DownloadError("Instagram: пост не содержит видео")
            loader.download_post(post, target=shortcode)
            candidates = sorted(self.options.output_dir.rglob(f"{shortcode}*.mp4"))
            if not candidates:
                raise DownloadError("Instagram: файл не создан")
            fp = candidates[0]
            info = VideoInfo(
                id=shortcode,
                title=post.title or "instagram_video",
                author=post.owner_username,
                duration=post.video_duration,
                description=(post.caption or "")[:2000],
                upload_date=post.date_utc.strftime("%Y%m%d"),
                url=url,
                platform=self.name,
            )
            self._save_metadata(info, fp)
            return DownloadResult(url=url, success=True, filepath=fp, info=info)
        except Exception as exc:  # noqa: BLE001
            raise DownloadError(f"Instagram/instaloader: {exc}") from exc

    @staticmethod
    def _guess_username(cookies_file: Path) -> str:
        # грубо: имя файла <username>.cookies.txt
        return cookies_file.name.split(".")[0] or "unknown"