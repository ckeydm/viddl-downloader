"""Простейший GUI на Tkinter (в стандартной библиотеке)."""
from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from viddl.downloader.base import DownloadOptions
from viddl.downloader.registry import get_downloader
from viddl.utils.ffmpeg import require_ffmpeg


def run_gui() -> None:
    require_ffmpeg(hard=False)

    root = tk.Tk()
    root.title("viddl — загрузчик видео")
    root.geometry("640x420")

    tk.Label(root, text="URL (по одному на строку):").pack(anchor="w", padx=10, pady=(10, 0))
    text = tk.Text(root, height=8)
    text.pack(fill="x", padx=10)

    row = tk.Frame(root); row.pack(fill="x", padx=10, pady=6)
    tk.Label(row, text="Качество:").pack(side="left")
    quality = ttk.Combobox(row, values=["best", "1080p", "720p", "480p", "audio"],
                           state="readonly", width=10)
    quality.set("best")
    quality.pack(side="left", padx=6)

    audio_var = tk.BooleanVar(value=False)
    tk.Checkbutton(row, text="Только аудио", variable=audio_var).pack(side="left", padx=6)

    out_row = tk.Frame(root); out_row.pack(fill="x", padx=10, pady=6)
    tk.Label(out_row, text="Папка:").pack(side="left")
    out_var = tk.StringVar(value=str(Path("./downloads").resolve()))
    tk.Entry(out_row, textvariable=out_var).pack(side="left", fill="x", expand=True, padx=6)
    tk.Button(out_row, text="…",
              command=lambda: out_var.set(filedialog.askdirectory() or out_var.get())
              ).pack(side="left")

    log = tk.Text(root, height=10, state="disabled")
    log.pack(fill="both", expand=True, padx=10, pady=6)

    def _log(msg: str) -> None:
        log.configure(state="normal")
        log.insert("end", msg + "\n")
        log.see("end")
        log.configure(state="disabled")

    def _worker(urls: list[str], options: DownloadOptions) -> None:
        for u in urls:
            _log(f"→ {u}")
            try:
                cls = get_downloader(u)
                res = cls(options).download(u)
                if res.success:
                    _log(f"✅ {res.filepath}")
                else:
                    _log(f"❌ {res.error}")
            except Exception as exc:  # noqa: BLE001
                _log(f"❌ {exc}")
        _log("Готово.")
        root.after(0, lambda: messagebox.showinfo("viddl", "Очередь обработана"))

    def on_start() -> None:
        urls = [l.strip() for l in text.get("1.0", "end").splitlines()
                if l.strip() and not l.strip().startswith("#")]
        if not urls:
            messagebox.showwarning("viddl", "Добавьте хотя бы один URL")
            return
        options = DownloadOptions(
            quality="audio" if audio_var.get() else quality.get(),
            output_dir=Path(out_var.get()),
            audio_only=audio_var.get(),
        )
        threading.Thread(target=_worker, args=(urls, options), daemon=True).start()

    tk.Button(root, text="Скачать", command=on_start,
              bg="#2e7d32", fg="white").pack(pady=6)

    root.mainloop()