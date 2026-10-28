# viddl/downloader/__init__.py
from viddl.downloader.base import (
    BaseDownloader, DownloadError, DownloadOptions, DownloadResult, VideoInfo,
)
from viddl.downloader.registry import get_downloader, list_platforms, register

__all__ = [
    "BaseDownloader", "DownloadError", "DownloadOptions",
    "DownloadResult", "VideoInfo",
    "get_downloader", "list_platforms", "register",
]