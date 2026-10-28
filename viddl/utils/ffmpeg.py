"""Проверка наличия ffmpeg."""
from __future__ import annotations

import shutil
import sys


def is_ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def require_ffmpeg(hard: bool = False) -> bool:
    """Проверить ffmpeg. При hard=True — выйти с ошибкой."""
    if is_ffmpeg_available():
        return True
    msg = (
        "⚠️  ffmpeg не найден. Извлечение звука и склейка видео работать не будут.\n"
        "   Установите: https://ffmpeg.org/download.html\n"
        "   Linux: sudo apt install ffmpeg | macOS: brew install ffmpeg | "
        "Windows: choco install ffmpeg"
    )
    print(msg, file=sys.stderr)
    if hard:
        raise SystemExit(1)
    return False