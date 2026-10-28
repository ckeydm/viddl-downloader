"""Конфигурация (YAML/JSON)."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore


@dataclass
class Config:
    quality: str = "best"
    output_dir: Path = Path("./downloads")
    audio_only: bool = False
    cookies_file: Optional[Path] = None
    proxy: Optional[str] = None
    save_metadata: bool = True
    skip_existing: bool = True
    concurrent: int = 2
    retries: int = 3
    log_file: Optional[Path] = Path("./viddl.log")
    verbose: bool = False

    @classmethod
    def load(cls, path: Path) -> "Config":
        if not path.exists():
            raise FileNotFoundError(f"Конфиг не найден: {path}")
        text = path.read_text(encoding="utf-8")
        if path.suffix in (".yaml", ".yml"):
            if yaml is None:
                raise RuntimeError("Установите PyYAML: pip install pyyaml")
            data = yaml.safe_load(text) or {}
        elif path.suffix == ".json":
            data = json.loads(text)
        else:
            raise ValueError("Поддерживаются только .yaml/.yml/.json")
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        kwargs: dict[str, Any] = {}
        for key, f in cls.__dataclass_fields__.items():  # type: ignore[attr-defined]
            if key not in data:
                continue
            val = data[key]
            if key in ("output_dir", "cookies_file", "log_file") and val:
                val = Path(val)
            kwargs[key] = val
        return cls(**kwargs)