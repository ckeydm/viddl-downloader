"""Санитизация имён файлов (кросс-платформенно)."""
from __future__ import annotations

import re

# запрещённые в Windows + управляющие символы
_ILLEGAL = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_WS = re.compile(r"\s+")
# зарезервированные имена Windows
_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}

MAX_LEN = 180


def sanitize_filename(name: str, *, replacement: str = "_") -> str:
    """Убрать опасные символы, обрезать длину, защитить от reserved-имён."""
    if not name:
        return "untitled"
    name = _ILLEGAL.sub(replacement, name)
    name = _WS.sub(" ", name).strip(" .")
    # Windows не любит имена, заканчивающиеся точкой
    name = name.rstrip(". ")
    if name.upper().split(".")[0] in _RESERVED:
        name = f"_{name}"
    if len(name) > MAX_LEN:
        base, dot, ext = name.rpartition(".")
        if dot and len(ext) <= 6:
            name = base[: MAX_LEN - len(ext) - 1] + "." + ext
        else:
            name = name[:MAX_LEN]
    return name or "untitled"