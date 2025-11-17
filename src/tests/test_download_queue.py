import asyncio

import pytest

from src.queue.download_queue import DownloadQueue


@pytest.fixture
def test_queue() -> DownloadQueue:
    """
    Fixture that provides DownloadQueue instance for tests.
    :return: DownloadQueue instance for tests.
    """
    return DownloadQueue()


VALID_YOUTUBE_URLS = ["https://youtu.be/dQw4w9WgXcQ?si=52ngrNGc_WNyEkUb",
                      "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ",
                      "http://youtu.be/dQw4w9WgXcQ?si=52ngrNGc_WNyEkUb", ]

INVALID_YOUTUBE_URLS = ["https://example.com/video", "not a url", "ftp://youtu.be/invalid", ]


# Tests for add_video
@pytest.mark.parametrize("url", VALID_YOUTUBE_URLS)
def test_add_video_valid_urls(url: str, test_queue: DownloadQueue) -> None:
    """Test adding videos with valid YouTube URLs."""
    result = asyncio.run(test_queue.add_video(url, 720, "Test Video Title"))
    assert "added to queue" in result.lower()


def test_add_video_queue_limit(test_queue: DownloadQueue) -> None:
    """Test that queue respects 5 item limit."""
    for i in range(5):
        asyncio.run(test_queue.add_video(f"https://youtu.be/test{i}", 720, f"Test Video {i}"))
    result = asyncio.run(test_queue.add_video("https://youtu.be/test6", 720, "Test Video 6"))
    assert "queue" in result.lower() and "limit" in result.lower()


@pytest.mark.parametrize("quality", [144, 240, 360, 480, 720, 1080])
def test_add_video_different_qualities(quality: int, test_queue: DownloadQueue) -> None:
    """Test adding videos with different quality settings."""
    result = asyncio.run(test_queue.add_video("https://youtu.be/dQw4w9WgXcQ", quality, f"Test Video {quality}p"))
    assert "added to queue" in result.lower()


@pytest.mark.parametrize("invalid_input", [None, 123, [], {}, 12.34, True, False])
def test_add_video_invalid_input_types(invalid_input) -> None:
    """Test handling of invalid input types for URL parameter."""
    test_queue = DownloadQueue()
    result = asyncio.run(test_queue.add_video(invalid_input, 720, "Test Video"))
    assert "invalid" in result.lower() or "error" in result.lower()


def test_add_video_empty_url() -> None:
    """Test handling of empty URL string."""
    test_queue = DownloadQueue()
    result = asyncio.run(test_queue.add_video("", 720, "Test Video"))
    assert "invalid" in result.lower() or "empty" in result.lower()


@pytest.mark.parametrize("invalid_input", [None, 123, [], {}, 12.34, "240", True, False])
def test_add_video_invalid_qualities(invalid_input, test_queue: DownloadQueue) -> None:
    """Test handling of invalid quality values."""
    result = asyncio.run(test_queue.add_video("https://youtu.be/dQw4w9WgXcQ", invalid_input, "Test Video"))
    assert "incorrect" in result.lower() or "invalid" in result.lower() or "error" in result.lower()


def test_add_video_empty_quality(test_queue: DownloadQueue) -> None:
    """Test handling of empty quality parameter."""
    result = asyncio.run(test_queue.add_video("https://youtu.be/dQw4w9WgXcQ", "", "Test Video"))
    assert "incorrect" in result.lower() or "invalid" in result.lower() or "error" in result.lower()


def test_add_video_duplicate_same_quality(test_queue: DownloadQueue) -> None:
    """Test that adding the same video with same quality is detected as duplicate."""
    url = "https://youtu.be/dQw4w9WgXcQ"
    asyncio.run(test_queue.add_video(url, 720, "Test Video"))
    result = asyncio.run(test_queue.add_video(url, 720, "Test Video"))
    assert "already" in result.lower()


def test_add_video_duplicate_different_quality(test_queue: DownloadQueue) -> None:
    """Test that the same video can be added with different qualities."""
    url = "https://youtu.be/dQw4w9WgXcQ"
    asyncio.run(test_queue.add_video(url, 720, "Test Video 720p"))
    result = asyncio.run(test_queue.add_video(url, 1080, "Test Video 1080p"))
    assert "added to queue" in result.lower()


# Tests for add_mp3_audio
@pytest.mark.parametrize("url", VALID_YOUTUBE_URLS)
def test_add_mp3_audio_valid_urls(url: str, test_queue: DownloadQueue) -> None:
    """Test adding MP3 audio with valid YouTube URLs."""
    result = asyncio.run(test_queue.add_mp3_audio(url, "Test Audio Title"))
    assert "added to queue" in result.lower()


def test_add_mp3_audio_queue_limit(test_queue: DownloadQueue) -> None:
    """Test that MP3 queue respects 5 item limit."""
    for i in range(5):
        asyncio.run(test_queue.add_mp3_audio(f"https://youtu.be/test{i}", f"Test Audio {i}"))
    result = asyncio.run(test_queue.add_mp3_audio("https://youtu.be/test6", "Test Audio 6"))
    assert "queue" in result.lower() and ("full" in result.lower() or "limit" in result.lower())


@pytest.mark.parametrize("invalid_input", [None, 123, [], {}, 12.34, True, False])
def test_add_mp3_audio_invalid_input_types(invalid_input, test_queue: DownloadQueue) -> None:
    """Test handling of invalid input types for MP3 URL parameter."""
    result = asyncio.run(test_queue.add_mp3_audio(invalid_input, "Test Audio"))
    assert "invalid" in result.lower() or "error" in result.lower()


def test_add_mp3_audio_empty_url(test_queue: DownloadQueue) -> None:
    """Test handling of empty URL string for MP3."""
    result = asyncio.run(test_queue.add_mp3_audio("", "Test Audio"))
    assert "invalid" in result.lower() or "empty" in result.lower()


# Tests for add_wav_audio
@pytest.mark.parametrize("url", VALID_YOUTUBE_URLS)
def test_add_wav_audio_valid_urls(url: str, test_queue: DownloadQueue) -> None:
    """Test adding WAV audio with valid YouTube URLs."""
    result = asyncio.run(test_queue.add_wav_audio(url, "Test Audio Title"))
    assert "added to queue" in result.lower()


def test_add_wav_audio_queue_limit(test_queue: DownloadQueue) -> None:
    """Test that WAV queue respects 5 item limit."""
    for i in range(5):
        asyncio.run(test_queue.add_wav_audio(f"https://youtu.be/test{i}", f"Test Audio {i}"))
    result = asyncio.run(test_queue.add_wav_audio("https://youtu.be/test6", "Test Audio 6"))
    assert "queue" in result.lower() and ("full" in result.lower() or "limit" in result.lower())


@pytest.mark.parametrize("invalid_input", [None, 123, [], {}, 12.34, True, False])
def test_add_wav_audio_invalid_input_types(invalid_input, test_queue: DownloadQueue) -> None:
    """Test handling of invalid input types for WAV URL parameter."""
    result = asyncio.run(test_queue.add_wav_audio(invalid_input, "Test Audio"))
    assert "invalid" in result.lower() or "error" in result.lower()


def test_add_wav_audio_empty_url(test_queue: DownloadQueue) -> None:
    """Test handling of empty URL string for WAV."""
    result = asyncio.run(test_queue.add_wav_audio("", "Test Audio"))
    assert "invalid" in result.lower() or "empty" in result.lower()


# Tests for add_thumbnail
@pytest.mark.parametrize("url", VALID_YOUTUBE_URLS)
def test_add_thumbnail_valid_urls(url: str, test_queue: DownloadQueue) -> None:
    """Test adding thumbnails with valid YouTube URLs."""
    result = asyncio.run(test_queue.add_thumbnail(url, "Test Thumbnail Title"))
    assert "added to queue" in result.lower()


def test_add_thumbnail_queue_limit(test_queue: DownloadQueue) -> None:
    """Test that thumbnail queue respects 5 item limit."""
    for i in range(5):
        asyncio.run(test_queue.add_thumbnail(f"https://youtu.be/test{i}", f"Test Thumbnail {i}"))
    result = asyncio.run(test_queue.add_thumbnail("https://youtu.be/test6", "Test Thumbnail 6"))
    assert "queue" in result.lower() and ("full" in result.lower() or "limit" in result.lower())


@pytest.mark.parametrize("invalid_input", [None, 123, [], {}, 12.34, True, False])
def test_add_thumbnail_invalid_input_types(invalid_input, test_queue: DownloadQueue) -> None:
    """Test handling of invalid input types for thumbnail URL parameter."""
    result = asyncio.run(test_queue.add_thumbnail(invalid_input, "Test Thumbnail"))
    assert "invalid" in result.lower() or "error" in result.lower()


def test_add_thumbnail_empty_url(test_queue: DownloadQueue) -> None:
    """Test handling of empty URL string for thumbnail."""
    result = asyncio.run(test_queue.add_thumbnail("", "Test Thumbnail"))
    assert "invalid" in result.lower() or "empty" in result.lower()


# Tests for add_tags
@pytest.mark.parametrize("url", VALID_YOUTUBE_URLS)
def test_add_tags_valid_urls(url: str, test_queue: DownloadQueue) -> None:
    """Test adding tags extraction with valid YouTube URLs."""
    result = asyncio.run(test_queue.add_tags(url, "Test Tags Title"))
    assert "added to queue" in result.lower()


def test_add_tags_queue_limit(test_queue: DownloadQueue) -> None:
    """Test that tags queue respects 5 item limit."""
    for i in range(5):
        asyncio.run(test_queue.add_tags(f"https://youtu.be/test{i}", f"Test Tags {i}"))
    result = asyncio.run(test_queue.add_tags("https://youtu.be/test6", "Test Tags 6"))
    assert "queue" in result.lower() and ("full" in result.lower() or "limit" in result.lower())


@pytest.mark.parametrize("invalid_input", [None, 123, [], {}, 12.34, True, False])
def test_add_tags_invalid_input_types(invalid_input, test_queue: DownloadQueue) -> None:
    """Test handling of invalid input types for tags URL parameter."""
    result = asyncio.run(test_queue.add_tags(invalid_input, "Test Tags"))
    assert "invalid" in result.lower() or "error" in result.lower()


def test_add_tags_empty_url(test_queue: DownloadQueue) -> None:
    """Test handling of empty URL string for tags."""
    result = asyncio.run(test_queue.add_tags("", "Test Tags"))
    assert "invalid" in result.lower() or "empty" in result.lower()


# Tests for start_queue
def test_start_queue_mp4_empty(test_queue: DownloadQueue) -> None:
    """Test starting empty MP4 queue."""
    assert asyncio.run(test_queue.start_queue("mp4")) == "Nothing to download, queue is empty."


def test_start_queue_mp3_empty(test_queue: DownloadQueue) -> None:
    """Test starting empty MP3 queue."""
    assert asyncio.run(test_queue.start_queue("mp3")) == "Nothing to download, queue is empty."


def test_start_queue_wav_empty(test_queue: DownloadQueue) -> None:
    """Test starting empty WAV queue."""
    assert asyncio.run(test_queue.start_queue("wav")) == "Nothing to download, queue is empty."


def test_start_queue_jpg_empty(test_queue: DownloadQueue) -> None:
    """Test starting empty JPG queue."""
    assert asyncio.run(test_queue.start_queue("jpg")) == "Nothing to download, queue is empty."


def test_start_queue_csv_empty(test_queue: DownloadQueue) -> None:
    """Test starting empty CSV queue."""
    assert asyncio.run(test_queue.start_queue("csv")) == "Nothing to download, queue is empty."
