📥 viddl — кроссплатформенный загрузчик видео

Стек: Python 3.10+ · CLI (Click) + GUI (Tkinter) · yt-dlp · Instaloader · MIT License

Универсальная утилита для скачивания видео и аудио с популярных платформ через один интерфейс — с выбором качества, пакетной загрузкой и понятной обработкой ошибок.


📋 О проекте

viddl — консольный (и опционально графический) загрузчик медиа на Python. Под капотом — связка из yt-dlp (основной движок), instaloader (fallback для Instagram) и собственного слоя-обёртки, который нормализует работу с разными источниками: единый API, единый формат имён файлов, единые метаданные.

Проект задуман как расширяемая архитектура: каждая платформа — отдельный класс, наследующий BaseDownloader. Добавить новую платформу — значит написать 40–50 строк и зарегистрировать класс в реестре.

✨ Возможности

🎯 Основные функции

· Мультиплатформенность: YouTube, TikTok, Instagram, Twitter/X, Facebook, Vimeo, Reddit, Twitch (клипы), Dailymotion + generic (fallback на yt-dlp для любых других сайтов)
· Автоопределение платформы: движок сам выбирает нужный загрузчик по домену URL
· Гибкий выбор качества: best, 1080p, 720p, 480p, audio-only (MP3 через ffmpeg)
· Пакетная обработка: одиночный URL или файл со списком (по одному на строку)
· Параллельные загрузки: ограничение concurrent-задач через ThreadPoolExecutor
· Докачка при обрыве: continuedl + download_archive — повторный запуск не перекачивает уже скачанное
· Метаданные в JSON: название, автор, длительность, описание, дата, платформа — рядом с каждым файлом
· Прогресс-бар (tqdm) и подробное логирование в файл

🔧 Расширенные возможности

· Cookies-файл (Netscape format) для приватных платформ
· Прокси HTTP / HTTPS / SOCKS4 / SOCKS5
· Конфигурация через YAML или JSON
· Валидация наличия ffmpeg с предупреждением
· Санитизация имён файлов (кросс-платформенно, с учётом Windows-reserved имён)
· Опция «не скачивать, если файл уже существует» по ID
· Unit-тесты для парсинга URL, реестра и санитизации

🎨 Интерфейс

· CLI на Click — с таблицей флагов, цветными статусами и итоговой сводкой
· GUI на Tkinter — минималистичный, без внешних зависимостей: поле URL-ов, выбор качества, папка назначения и лог-окно

📖 Использование

Базовый запуск

```bash
# Одиночное видео
viddl --url "https://youtu.be/dQw4w9WgXcQ" --quality 720p --output ./videos

# Список URL + только аудио
viddl --list urls.txt --audio-only

# Instagram Reel с cookies и прокси
viddl --url "https://www.instagram.com/reel/XXXX/" \
      --cookies cookies.txt --proxy socks5://127.0.0.1:1080

# Графический интерфейс
viddl --gui

# Конфиг из YAML
viddl --config config.yaml --url "https://www.tiktok.com/@user/video/123"
```

Флаги CLI

Флаг Назначение
--url, -u одиночный URL
--list, -l файл со списком URL
--quality, -q best \| 1080p \| 720p \| 480p \| audio
--output, -o папка сохранения (по умолчанию ./downloads)
--audio-only только звук → MP3
--cookies файл cookies (Netscape)
--proxy http:// или socks5://
--concurrent параллельных загрузок
--retries повторов на ошибку
--no-metadata не сохранять JSON
--no-skip-existing перекачивать поверх
--config YAML/JSON-конфиг
--gui запустить GUI
--platforms список поддерживаемых платформ
--verbose, -v подробный лог

Формат имени файла

```
{platform}_{author}_{title}_{id}.{ext}
```

Все запрещённые символы (<>:"/\|?*, управляющие) заменяются на _, имена длиннее 180 символов обрезаются с сохранением расширения, CON/PRN/NUL и прочие Windows-reserved имена экранируются.

🎯 Примеры использования

YouTube-плейлист в 720p:

```bash
viddl --url "https://www.youtube.com/playlist?list=PL..." -q 720p -o ./playlist
```

Пакет TikTok-видео из файла:

```bash
viddl --list tik_tok_urls.txt --concurrent 4 -o ./tiktok
```

Только звук с Twitter:

```bash
viddl --url "https://x.com/user/status/123" --audio-only
```

Приватный Instagram-пост:

```bash
viddl --url "https://www.instagram.com/p/XXXX/" --cookies instagram.cookies.txt
```

🗂 Структура проекта

```
viddl/
├── viddl/
│   ├── cli.py                # CLI на Click
│   ├── gui.py                # GUI на Tkinter
│   ├── config.py             # YAML/JSON-конфиг
│   ├── downloader/
│   │   ├── base.py           # BaseDownloader, DownloadResult, VideoInfo
│   │   ├── registry.py       # Автоопределение платформы + register()
│   │   ├── youtube.py
│   │   ├── tiktok.py
│   │   ├── instagram.py      # yt-dlp + instaloader fallback
│   │   ├── twitter.py
│   │   ├── facebook.py
│   │   ├── vimeo.py
│   │   ├── reddit.py
│   │   ├── twitch.py
│   │   ├── dailymotion.py
│   │   └── generic.py        # fallback: yt-dlp угадывает сам
│   └── utils/
│       ├── sanitize.py       # безопасные имена файлов
│       ├── ffmpeg.py         # проверка ffmpeg
│       ├── logging_setup.py
│       └── progress.py
├── tests/
├── config.example.yaml
├── requirements.txt
├── setup.py
└── README.md
```

Расширение: своя платформа

```python
from viddl.downloader.base import BaseDownloader, DownloadResult, VideoInfo
from viddl.downloader.registry import register


class MyPlatform(BaseDownloader):
    name = "myplatform"
    domains = ("myplatform.com",)

    def download(self, url: str) -> DownloadResult:
        ...  # ваша логика: yt_dlp или requests
        return DownloadResult(url=url, success=True, filepath=..., info=...)


register(MyPlatform)   # платформа сразу становится доступна
```

🛡 Безопасность и этика

· Поддержка прокси для анонимности
· Опциональная ротация User-Agent через yt-dlp
· Задержки между запросами (ratelimit)
· Cookies-файл не копируется и не передаётся наружу
· Все метаданные хранятся локально, никакой телеметрии

⚠️ Дисклеймер

Проект создан для личного использования. Скачивание контента может нарушать пользовательские соглашения платформ. Автор не несёт ответственности за неправомерное использование. Запрещено применять для:

· массового парсинга,
· обхода платных подписок,
· обхода DRM,
· распространения чужого контента.

Использование — на ваш собственный риск. Проверяйте лицензии скачиваемого контента.

🤝 Вклад в проект

· Fork репозитория
· Создайте ветку: git checkout -b feature/amazing-feature
· Закоммитьте: git commit -m 'Add amazing feature'
· Push: git push origin feature/amazing-feature
· Откройте Pull Request

Перед PR прогоняйте pytest -q — все тесты должны зелёными.

📝 TODO

☐ Веб-интерфейс на FastAPI + простой фронтенд
☐ Уведомления в Telegram по завершении загрузки
☐ Поддержка YouTube-каналов (мониторинг новых видео)
☐ Пакетное скачивание из CSV с колонкой «качество»
☐ Автоматическая конвертация в MP4/H.264 для совместимости
☐ Экспорт отчёта о загрузках в CSV/JSON
☐ Docker-образ
☐ Мультиязычный интерфейс (RU/EN)

🌟 Благодарности

· yt-dlp — за универсальный движок
· instaloader — за работу с Instagram
· Click — за удобный CLI
· tqdm — за прогресс-бары
· Сообществу open-source за вдохновение

📄 Лицензия

MIT. См. файл LICENSE.

🧭 Быстрый старт

```bash
git clone <repo-url>
cd viddl
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m viddl --url "https://youtu.be/dQw4w9WgXcQ" -q 720p -o ./videos
```

Требуется ffmpeg для audio-only и склейки видео. Установка:
apt install ffmpeg · brew install ffmpeg · choco install ffmpeg

⭐ Если проект оказался полезен — поставьте звезду. Это лучший мотиватор развивать viddl дальше.