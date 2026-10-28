from viddl.downloader.registry import get_downloader, list_platforms
from viddl.downloader.youtube import YouTubeDownloader
from viddl.downloader.tiktok import TikTokDownloader
from viddl.downloader.instagram import InstagramDownloader
from viddl.downloader.generic import GenericDownloader


def test_youtube():
    assert get_downloader("https://youtu.be/abc") is YouTubeDownloader
    assert get_downloader("https://www.youtube.com/watch?v=abc") is YouTubeDownloader


def test_tiktok():
    assert get_downloader("https://www.tiktok.com/@u/video/1") is TikTokDownloader


def test_instagram():
    assert get_downloader("https://www.instagram.com/reel/xyz/") is InstagramDownloader


def test_generic_fallback():
    assert get_downloader("https://example.com/video.mp4") is GenericDownloader


def test_platforms_list():
    p = list_platforms()
    for expected in ("youtube", "tiktok", "instagram", "twitter",
                     "facebook", "vimeo", "reddit", "twitch", "dailymotion"):
        assert expected in p