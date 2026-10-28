"""Реестр загрузчиков и автоопределение платформы по URL."""
from __future__ import annotations

from typing import Type

from viddl.downloader.base import BaseDownloader
from viddl.downloader.youtube import YouTubeDownloader
from viddl.downloader.tiktok import TikTokDownloader
from viddl.downloader.instagram import InstagramDownloader
from viddl.downloader.twitter import TwitterDownloader
from viddl.downloader.facebook import FacebookDownloader
from viddl.downloader.vimeo import VimeoDownloader
from viddl.downloader.reddit import RedditDownloader
from viddl.downloader.twitch import TwitchDownloader
from viddl.downloader.dailymotion import DailymotionDownloader
from viddl.downloader.generic import GenericDownloader

#: Порядок важен: специфичные платформы — раньше generic
_DOWNLOADERS: list[Type[BaseDownloader]] = [
    YouTubeDownloader,
    TikTokDownloader,
    InstagramDownloader,
    TwitterDownloader,
    FacebookDownloader,
    VimeoDownloader,
    RedditDownloader,
    TwitchDownloader,
    DailymotionDownloader,
    GenericDownloader,  # fallback: yt-dlp сам разберётся
]


def register(downloader_cls: Type[BaseDownloader], *, prepend: bool = False) -> None:
    """Зарегистрировать новый загрузчик (для расширения)."""
    if prepend:
        _DOWNLOADERS.insert(0, downloader_cls)
    else:
        _DOWNLOADERS.append(downloader_cls)


def get_downloader(url: str) -> Type[BaseDownloader]:
    """Выбрать класс загрузчика для URL."""
    for cls in _DOWNLOADERS:
        try:
            if cls.supports(url):
                return cls
        except Exception:  # noqa: BLE001 — платформенный код не должен ронять реестр
            continue
    return GenericDownloader


def list_platforms() -> list[str]:
    return [cls.name for cls in _DOWNLOADERS]