"""Простой прогресс для пакетной загрузки."""
from __future__ import annotations

try:
    from tqdm import tqdm  # type: ignore
except ImportError:  # pragma: no cover
    tqdm = None  # type: ignore


def progress_iter(iterable, total=None, desc: str = "downloads"):
    if tqdm is not None:
        return tqdm(iterable, total=total, desc=desc)
    return iterable