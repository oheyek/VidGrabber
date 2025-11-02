import pytest

from src.thumbnail_downloader import ThumbnailDownloader
from src.video_info import VideoInfo

video_info = VideoInfo()
thumbnail_downloader = ThumbnailDownloader(video_info)

VALID_YOUTUBE_URLS = [
    "https://youtu.be/dQw4w9WgXcQ?si=52ngrNGc_WNyEkUb",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ",
    "http://youtu.be/dQw4w9WgXcQ?si=52ngrNGc_WNyEkUb",
    "http://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ&start_radio=1",
    "www.youtube.com/watch?v=dQw4w9WgXcQ",
]

INVALID_YOUTUBE_URLS = [
    "https://www.google.com/",
    "http://www.google.com/",
    "https://vimeo.com/123456",
    "ftp://youtube.com/watch?v=test",
]

@pytest.mark.asyncio
@pytest.mark.parametrize("url", VALID_YOUTUBE_URLS)
async def test_download_thumbnail_valid_links(url: str) -> None:
    """Test for downloading thumbnails with valid links"""
    result = await thumbnail_downloader.download_thumbnail(url)
    assert result == "Thumbnail download completed!"


@pytest.mark.asyncio
@pytest.mark.parametrize("url", INVALID_YOUTUBE_URLS)
async def test_download_thumbnail_invalid_links(url: str) -> None:
    """Test for downloading thumbnails with invalid links"""
    result = await thumbnail_downloader.download_thumbnail(url)
    assert result == "Invalid link provided."

@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_input", [None, 123, [], {}, 12.34])
async def test_download_thumbnail_invalid_input_types(invalid_input) -> None:
    """Test for downloading thumbnails with invalid YouTube URLs."""
    result = await thumbnail_downloader.download_thumbnail(invalid_input)
    assert result == "Invalid link provided."

@pytest.mark.asyncio
async def test_download_thumbnail_empty_url() -> None:
    """Test that empty string is rejected while downloading."""
    result = await thumbnail_downloader.download_thumbnail("")
    assert result == "Invalid link provided."