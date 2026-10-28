# viddl — кроссплатформенный загрузчик видео

CLI/GUI-приложение на Python 3.10+, скачивающее видео с **YouTube, TikTok,
Instagram, Twitter/X, Facebook, Vimeo, Reddit, Twitch (клипы), Dailymotion**
и любых других сайтов, которые умеет `yt-dlp`.

## ⚠️ Юридическое предупреждение

Софт предназначен **только для личного использования**. Скачивание контента
может нарушать пользовательские соглашения платформ. Автор не несёт
ответственности за неправомерное использование. Не используйте для
массового парсинга, обхода платных подписок или DRM.

## Установка

```bash
pip install -r requirements.txt
# или как пакет (создаст команду viddl)
pip install -e .
```

Требуется **ffmpeg** для извлечения аудио и склейки видео:
- Linux: `sudo apt install ffmpeg`
- macOS: `brew install ffmpeg`
- Windows: `choco install ffmpeg` или [скачать](https://ffmpeg.org/download.html)

## Использование

```bash
# Одиночное видео
viddl --url "https://youtu.be/dQw4w9WgXcQ" --quality 720p --output ./videos

# Список URL + только аудио + cookies
viddl --list urls.txt --audio-only --cookies cookies.txt

# Instagram Reel с прокси
viddl --url "https://www.instagram.com/reel/XXXX/" --proxy socks5://127.0.0.1:1080

# GUI
viddl --gui

# Конфиг из YAML
viddl --config config.yaml --url "https://www.tiktok.com/@user/video/123"
```

### Флаги

| Флаг | Описание |
|---|---|
| `--url, -u` | одиночный URL |
| `--list, -l` | файл со списком URL |
| `--quality, -q` | `best` \| `1080p` \| `720p` \| `480p` \| `audio` |
| `--output, -o` | папка сохранения (по умолчанию `./downloads`) |
| `--audio-only` | только звук → MP3 (нужен ffmpeg) |
| `--cookies` | файл cookies (Netscape) для приватных платформ |
| `--proxy` | `http://...` или `socks5://...` |
| `--no-metadata` | не сохранять JSON-метаданные |
| `--no-skip-existing` | не использовать archive (перекачивать) |
| `--concurrent` | параллельных загрузок (по умолчанию 2) |
| `--retries` | повторов на ошибку |
| `--config` | YAML/JSON-конфиг |
| `--gui` | графический интерфейс |
| `--platforms` | список поддерживаемых платформ |
| `--verbose, -v` | подробный лог |

## Формат имени файла

```
{platform}_{author}_{title}_{id}.{ext}
```

Санитизация удаляет `<>:"/\|?*`, управляющие символы, обрезает до 180 символов,
экранирует `CON/PRN/...`.

## Метаданные

При `save_metadata: true` рядом с видео сохраняется `*.mp4.json`:

```json
{
  "id": "dQw4w9WgXcQ",
  "title": "...",
  "author": "...",
  "duration": 212.0,
  "description": "...",
  "upload_date": "20091025",
  "url": "https://youtu.be/dQw4w9WgXcQ",
  "platform": "youtube"
}
```

## Обработка ошибок

Понятные сообщения для: приватных видео, гео-блоков, возрастных ограничений,
требования капчи, отсутствия видео. Обрыв соединения → продолжение загрузки
(`continuedl` + `retries`).

## Расширение (своя платформа)

```python
from viddl.downloader.base import BaseDownloader, DownloadResult, VideoInfo
from viddl.downloader.registry import register


class MyPlatform(BaseDownloader):
    name = "myplatform"
    domains = ("myplatform.com",)

    def download(self, url: str) -> DownloadResult:
        ...  # ваша логика, используйте yt_dlp или requests
        return DownloadResult(url=url, success=True, filepath=..., info=...)


register(MyPlatform)  # теперь get_downloader его увидит
```

## Тестирование

```bash
pytest -q
```

Ручная проверка: скачайте по 2–3 публичных видео с каждой платформы.

## Лицензия

MIT — см. [LICENSE](./LICENSE).

## Авторы

Сделано как учебный/утилитарный проект. Pull requests приветствуются.