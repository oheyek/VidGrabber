import pytest

from downloader import Downloader
from video_info import VideoInfo

video_info = VideoInfo()
downloader = Downloader(video_info)

VALID_YOUTUBE_URLS = ["https://youtu.be/dQw4w9WgXcQ?si=52ngrNGc_WNyEkUb",
                      "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ",
                      "http://youtu.be/dQw4w9WgXcQ?si=52ngrNGc_WNyEkUb",
                      "http://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ",
                      "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ&start_radio=1", ]

INVALID_YOUTUBE_URLS = ["https://www.google.com/", "http://www.google.com/", "https://vimeo.com/123456",
                        "ftp://youtube.com/watch?v=test", ]


@pytest.mark.parametrize("url", VALID_YOUTUBE_URLS)
def test_download_valid_links(url: str) -> None:
    """Test for downloading videos with valid links"""
    assert downloader.download_video(url, 144) == "Download completed!"


@pytest.mark.parametrize("url", INVALID_YOUTUBE_URLS)
def test_download_invalid_urls(url: str) -> None:
    """Test for downloading videos with invalid YouTube URLs."""
    assert downloader.download_video(url, 144) == "Invalid link provided."


@pytest.mark.parametrize("invalid_input", [None, 123, [], {}, 12.34])
def test_download_url_invalid_input_types(invalid_input) -> None:
    """Test for downloading videos with invalid YouTube URLs."""
    assert downloader.download_video(invalid_input, 144) == "Invalid link provided."


@pytest.mark.parametrize("invalid_input", [None, 123, [], {}, 12.34])
def test_download_video_invalid_qualities(invalid_input) -> None:
    """Test for downloading videos with invalid video qualities."""
    assert downloader.download_video("https://youtu.be/dQw4w9WgXcQ?si=52ngrNGc_WNyEkUb",
                                     invalid_input) == "Incorrect video quality."


def test_download_empty_url() -> None:
    """Test that empty string is rejected while downloading."""
    assert downloader.download_video("", 144) == "Invalid link provided."


def test_download_empty_quality() -> None:
    """Test that empty string is rejected while downloading."""
    assert downloader.download_video("https://youtu.be/dQw4w9WgXcQ?si=52ngrNGc_WNyEkUb",
                                     "") == "Incorrect video quality."
