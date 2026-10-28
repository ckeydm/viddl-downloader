"""Базовый класс загрузчика и общие структуры данных."""
from __future__ import annotations

import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from viddl.utils.sanitize import sanitize_filename

log = logging.getLogger(__name__)


class DownloadError(Exception):
    """Ошибка скачивания с понятным сообщением для пользователя."""


@dataclass
class VideoInfo:
    """Метаданные видео."""
    id: str
    title: str
    author: str
    duration: Optional[float] = None
    description: str = ""
    upload_date: Optional[str] = None
    url: str = ""
    platform: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "duration": self.duration,
            "description": self.description,
            "upload_date": self.upload_date,
            "url": self.url,
            "platform": self.platform,
        }


@dataclass
class DownloadResult:
    """Результат скачивания одной ссылки."""
    url: str
    success: bool
    filepath: Optional[Path] = None
    info: Optional[VideoInfo] = None
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "success": self.success,
            "filepath": str(self.filepath) if self.filepath else None,
            "info": self.info.to_dict() if self.info else None,
            "error": self.error,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


@dataclass
class DownloadOptions:
    """Параметры скачивания."""
    quality: str = "best"          # best | 1080p | 720p | 480p | audio
    output_dir: Path = Path("./downloads")
    audio_only: bool = False
    cookies_file: Optional[Path] = None
    proxy: Optional[str] = None
    save_metadata: bool = True
    skip_existing: bool = True
    retries: int = 3
    extra: dict[str, Any] = field(default_factory=dict)


class BaseDownloader(ABC):
    """Абстрактный загрузчик платформы."""

    #: человекочитаемое имя платформы
    name: str = "generic"
    #: список доменов, обрабатываемых этим загрузчиком
    domains: tuple[str, ...] = ()

    def __init__(self, options: DownloadOptions):
        self.options = options
        self.options.output_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def supports(cls, url: str) -> bool:
        from urllib.parse import urlparse
        host = urlparse(url).netloc.lower()
        return any(d in host for d in cls.domains)

    @abstractmethod
    def download(self, url: str) -> DownloadResult:
        """Скачать URL. Обязан вернуть DownloadResult."""
        ...

    # ------------- helpers -------------

    def _build_filename(self, info: VideoInfo, ext: str) -> Path:
        parts = [
            info.platform,
            info.author or "unknown",
            info.title or "untitled",
            info.id or "noid",
        ]
        base = sanitize_filename("_".join(parts))
        return self.options.output_dir / f"{base}.{ext}"

    def _save_metadata(self, info: VideoInfo, filepath: Path) -> None:
        if not self.options.save_metadata:
            return
        meta_path = filepath.with_suffix(filepath.suffix + ".json")
        try:
            meta_path.write_text(
                json.dumps(info.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            log.debug("Метаданные сохранены: %s", meta_path)
        except OSError as exc:
            log.warning("Не удалось сохранить метаданные %s: %s", meta_path, exc)