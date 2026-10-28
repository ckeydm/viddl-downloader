"""CLI на click."""
from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import click

from viddl.config import Config
from viddl.downloader.base import DownloadError, DownloadOptions, DownloadResult
from viddl.downloader.registry import get_downloader, list_platforms
from viddl.utils.ffmpeg import require_ffmpeg
from viddl.utils.logging_setup import setup_logging
from viddl.utils.progress import progress_iter


def _read_urls(url: str | None, list_file: Path | None) -> list[str]:
    urls: list[str] = []
    if url:
        urls.append(url)
    if list_file:
        if not list_file.exists():
            raise click.BadParameter(f"Файл со списком не найден: {list_file}")
        for line in list_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls


def _download_one(url: str, options: DownloadOptions) -> DownloadResult:
    cls = get_downloader(url)
    try:
        return cls(options).download(url)
    except DownloadError as exc:
        return DownloadResult(url=url, success=False, error=str(exc))
    except Exception as exc:  # noqa: BLE001
        return DownloadResult(url=url, success=False, error=f"Unhandled: {exc}")


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--url", "-u", help="Одиночный URL")
@click.option("--list", "-l", "list_file", type=click.Path(path_type=Path),
              help="Файл со списком URL (по одному на строку)")
@click.option("--quality", "-q", default="best",
              type=click.Choice(["best", "1080p", "720p", "480p", "audio"]),
              help="Желаемое качество")
@click.option("--output", "-o", type=click.Path(path_type=Path), default=Path("./downloads"),
              help="Папка для сохранения")
@click.option("--audio-only", is_flag=True, default=False, help="Только аудио (MP3)")
@click.option("--cookies", type=click.Path(path_type=Path), default=None,
              help="Файл cookies (Netscape format) для приватных платформ")
@click.option("--proxy", default=None, help="Прокси, напр. socks5://127.0.0.1:1080")
@click.option("--no-metadata", is_flag=True, default=False, help="Не сохранять JSON-метаданные")
@click.option("--no-skip-existing", is_flag=True, default=False,
              help="Скачивать даже если файл уже был")
@click.option("--concurrent", type=int, default=2, help="Параллельных загрузок")
@click.option("--retries", type=int, default=3, help="Количество повторов")
@click.option("--log", "log_file", type=click.Path(path_type=Path), default=Path("./viddl.log"))
@click.option("--verbose", "-v", is_flag=True, default=False)
@click.option("--config", "config_path", type=click.Path(path_type=Path), default=None)
@click.option("--gui", is_flag=True, default=False, help="Запустить графический интерфейс")
@click.option("--platforms", is_flag=True, default=False, help="Показать поддерживаемые платформы")
def main(
    url: str | None,
    list_file: Path | None,
    quality: str,
    output: Path,
    audio_only: bool,
    cookies: Path | None,
    proxy: str | None,
    no_metadata: bool,
    no_skip_existing: bool,
    concurrent: int,
    retries: int,
    log_file: Path,
    verbose: bool,
    config_path: Path | None,
    gui: bool,
    platforms: bool,
) -> None:
    """viddl — кроссплатформенный загрузчик видео."""

    if platforms:
        click.echo("Поддерживаемые платформы:")
        for p in list_platforms():
            click.echo(f"  • {p}")
        return

    if gui:
        from viddl.gui import run_gui
        run_gui()
        return

    # загрузка конфига
    cfg = Config()
    if config_path:
        cfg = Config.load(config_path)

    # CLI перекрывает конфиг
    cfg.quality = quality or cfg.quality
    cfg.output_dir = output if output != Path("./downloads") else cfg.output_dir
    cfg.audio_only = audio_only or cfg.audio_only
    cfg.cookies_file = cookies or cfg.cookies_file
    cfg.proxy = proxy or cfg.proxy
    cfg.save_metadata = not no_metadata and cfg.save_metadata
    cfg.skip_existing = not no_skip_existing and cfg.skip_existing
    cfg.concurrent = concurrent or cfg.concurrent
    cfg.retries = retries or cfg.retries
    cfg.log_file = log_file or cfg.log_file
    cfg.verbose = verbose or cfg.verbose

    setup_logging(cfg.log_file, cfg.verbose)
    require_ffmpeg(hard=cfg.audio_only)

    urls = _read_urls(url, list_file)
    if not urls:
        click.echo("❌ Не передано ни одного URL. Используйте --url или --list.", err=True)
        sys.exit(2)

    options = DownloadOptions(
        quality=cfg.quality,
        output_dir=cfg.output_dir,
        audio_only=cfg.audio_only,
        cookies_file=cfg.cookies_file,
        proxy=cfg.proxy,
        save_metadata=cfg.save_metadata,
        skip_existing=cfg.skip_existing,
        retries=cfg.retries,
    )

    click.echo(f"→ Загрузок в очереди: {len(urls)} | качество: {cfg.quality} | "
               f"папка: {cfg.output_dir}")

    results: list[DownloadResult] = []
    with ThreadPoolExecutor(max_workers=max(1, cfg.concurrent)) as pool:
        futures = {pool.submit(_download_one, u, options): u for u in urls}
        for fut in progress_iter(as_completed(futures), total=len(futures), desc="viddl"):
            res = fut.result()
            results.append(res)
            if res.success:
                click.echo(f"✅ {res.url}\n   → {res.filepath}")
            else:
                click.echo(f"❌ {res.url}\n   ! {res.error}", err=True)

    ok = sum(1 for r in results if r.success)
    click.echo(f"\nИтого: {ok}/{len(results)} успешно.")


if __name__ == "__main__":
    main()