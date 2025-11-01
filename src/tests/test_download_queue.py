import pytest
import asyncio

from src.queue.download_queue import DownloadQueue

VALID_YOUTUBE_URLS = [
    "https://youtu.be/dQw4w9WgXcQ?si=52ngrNGc_WNyEkUb",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ",
    "http://youtu.be/dQw4w9WgXcQ?si=52ngrNGc_WNyEkUb",
]

INVALID_YOUTUBE_URLS = [
    "https://www.google.com/",
    "http://www.google.com/",
    "https://vimeo.com/123456",
    "ftp://youtube.com/watch?v=test",
]


# Tests for add_video
@pytest.mark.parametrize("url", VALID_YOUTUBE_URLS)
def test_add_video_valid_urls(url: str) -> None:
    """Test adding valid video URLs to queue."""
    test_queue = DownloadQueue()
    assert test_queue.add_video(url, 240) == "Video added to queue"


def test_add_video_queue_limit() -> None:
    """Test that video queue limit is enforced."""
    test_queue = DownloadQueue()
    for i in range(5):
        test_queue.add_video(f"https://youtu.be/test{i}", 240)
    assert test_queue.add_video("https://youtu.be/test6", 240) == "Queue limit reached."


@pytest.mark.parametrize("quality", [144, 240, 360, 480, 720, 1080])
def test_add_video_different_qualities(quality: int) -> None:
    """Test adding videos with different qualities."""
    test_queue = DownloadQueue()
    assert test_queue.add_video(VALID_YOUTUBE_URLS[0], quality) == "Video added to queue"


@pytest.mark.parametrize("invalid_input", [None, 123, [], {}, 12.34, True, False])
def test_add_video_invalid_input_types(invalid_input) -> None:
    """Test adding videos with invalid input types."""
    test_queue = DownloadQueue()
    assert test_queue.add_video(invalid_input, 240) == "Invalid link provided."


def test_add_video_empty_url() -> None:
    """Test adding empty string as URL."""
    test_queue = DownloadQueue()
    assert test_queue.add_video("", 240) == "Invalid link provided."


@pytest.mark.parametrize("invalid_input", [None, 123, [], {}, 12.34, "240", True, False])
def test_add_video_invalid_qualities(invalid_input) -> None:
    """Test adding videos with invalid quality types."""
    test_queue = DownloadQueue()
    assert test_queue.add_video(VALID_YOUTUBE_URLS[0], invalid_input) == "Incorrect video quality."


def test_add_video_empty_quality() -> None:
    """Test adding video with empty quality."""
    test_queue = DownloadQueue()
    assert test_queue.add_video(VALID_YOUTUBE_URLS[0], "") == "Incorrect video quality."

def test_add_video_duplicate_same_quality() -> None:
    """Test adding duplicate video with same quality."""
    test_queue = DownloadQueue()
    test_queue.add_video(VALID_YOUTUBE_URLS[0], 240)
    assert test_queue.add_video(VALID_YOUTUBE_URLS[0], 240) == "Video with this quality already in queue."


def test_add_video_duplicate_different_quality() -> None:
    """Test adding same video with different quality."""
    test_queue = DownloadQueue()
    assert test_queue.add_video(VALID_YOUTUBE_URLS[0], 240) == "Video added to queue"
    assert test_queue.add_video(VALID_YOUTUBE_URLS[0], 480) == "Video added to queue"



# Tests for add_mp3_audio
@pytest.mark.parametrize("url", VALID_YOUTUBE_URLS)
def test_add_mp3_audio_valid_urls(url: str) -> None:
    """Test adding valid URLs to MP3 queue."""
    test_queue = DownloadQueue()
    assert test_queue.add_mp3_audio(url) == "Audio added to queue"


def test_add_mp3_audio_queue_limit() -> None:
    """Test that MP3 queue limit is enforced."""
    test_queue = DownloadQueue()
    for i in range(5):
        test_queue.add_mp3_audio(f"https://youtu.be/test{i}")
    assert test_queue.add_mp3_audio("https://youtu.be/test6") == "Queue limit reached."


@pytest.mark.parametrize("invalid_input", [None, 123, [], {}, 12.34, True, False])
def test_add_mp3_audio_invalid_input_types(invalid_input) -> None:
    """Test adding MP3 audio with invalid input types."""
    test_queue = DownloadQueue()
    assert test_queue.add_mp3_audio(invalid_input) == "Invalid link provided."


def test_add_mp3_audio_empty_url() -> None:
    """Test adding empty string to MP3 queue."""
    test_queue = DownloadQueue()
    assert test_queue.add_mp3_audio("") == "Invalid link provided."


# Tests for add_wav_audio
@pytest.mark.parametrize("url", VALID_YOUTUBE_URLS)
def test_add_wav_audio_valid_urls(url: str) -> None:
    """Test adding valid URLs to WAV queue."""
    test_queue = DownloadQueue()
    assert test_queue.add_wav_audio(url) == "Audio added to queue"


def test_add_wav_audio_queue_limit() -> None:
    """Test that WAV queue limit is enforced."""
    test_queue = DownloadQueue()
    for i in range(5):
        test_queue.add_wav_audio(f"https://youtu.be/test{i}")
    assert test_queue.add_wav_audio("https://youtu.be/test6") == "Queue limit reached."


@pytest.mark.parametrize("invalid_input", [None, 123, [], {}, 12.34, True, False])
def test_add_wav_audio_invalid_input_types(invalid_input) -> None:
    """Test adding WAV audio with invalid input types."""
    test_queue = DownloadQueue()
    assert test_queue.add_wav_audio(invalid_input) == "Invalid link provided."


def test_add_wav_audio_empty_url() -> None:
    """Test adding empty string to WAV queue."""
    test_queue = DownloadQueue()
    assert test_queue.add_wav_audio("") == "Invalid link provided."


# Tests for add_thumbnail
@pytest.mark.parametrize("url", VALID_YOUTUBE_URLS)
def test_add_thumbnail_valid_urls(url: str) -> None:
    """Test adding valid URLs to thumbnail queue."""
    test_queue = DownloadQueue()
    assert test_queue.add_thumbnail(url) == "Thumbnail added to queue"


def test_add_thumbnail_queue_limit() -> None:
    """Test that thumbnail queue limit is enforced."""
    test_queue = DownloadQueue()
    for i in range(5):
        test_queue.add_thumbnail(f"https://youtu.be/test{i}")
    assert test_queue.add_thumbnail("https://youtu.be/test6") == "Queue limit reached."


@pytest.mark.parametrize("invalid_input", [None, 123, [], {}, 12.34, True, False])
def test_add_thumbnail_invalid_input_types(invalid_input) -> None:
    """Test adding thumbnails with invalid input types."""
    test_queue = DownloadQueue()
    assert test_queue.add_thumbnail(invalid_input) == "Invalid link provided."


def test_add_thumbnail_empty_url() -> None:
    """Test adding empty string to thumbnail queue."""
    test_queue = DownloadQueue()
    assert test_queue.add_thumbnail("") == "Invalid link provided."


# Tests for add_tags
@pytest.mark.parametrize("url", VALID_YOUTUBE_URLS)
def test_add_tags_valid_urls(url: str) -> None:
    """Test adding valid URLs to tags queue."""
    test_queue = DownloadQueue()
    assert test_queue.add_tags(url) == "Tags added to queue"


def test_add_tags_queue_limit() -> None:
    """Test that tags queue limit is enforced."""
    test_queue = DownloadQueue()
    for i in range(5):
        test_queue.add_tags(f"https://youtu.be/test{i}")
    assert test_queue.add_tags("https://youtu.be/test6") == "Queue limit reached."


@pytest.mark.parametrize("invalid_input", [None, 123, [], {}, 12.34, True, False])
def test_add_tags_invalid_input_types(invalid_input) -> None:
    """Test adding tags with invalid input types."""
    test_queue = DownloadQueue()
    assert test_queue.add_tags(invalid_input) == "Invalid link provided."


def test_add_tags_empty_url() -> None:
    """Test adding empty string to tags queue."""
    test_queue = DownloadQueue()
    assert test_queue.add_tags("") == "Invalid link provided."


# Tests for start_queue
def test_start_queue_mp4_empty() -> None:
    """Test starting empty MP4 queue."""
    test_queue = DownloadQueue()
    assert asyncio.run(test_queue.start_queue("mp4")) == "Nothing to download, queue is empty."


def test_start_queue_mp3_empty() -> None:
    """Test starting empty MP3 queue."""
    test_queue = DownloadQueue()
    assert asyncio.run(test_queue.start_queue("mp3")) == "Nothing to download, queue is empty."


def test_start_queue_wav_empty() -> None:
    """Test starting empty WAV queue."""
    test_queue = DownloadQueue()
    assert asyncio.run(test_queue.start_queue("wav")) == "Nothing to download, queue is empty."


def test_start_queue_jpg_empty() -> None:
    """Test starting empty JPG queue."""
    test_queue = DownloadQueue()
    assert asyncio.run(test_queue.start_queue("jpg")) == "Nothing to download, queue is empty."


def test_start_queue_csv_empty() -> None:
    """Test starting empty CSV queue."""
    test_queue = DownloadQueue()
    assert asyncio.run(test_queue.start_queue("csv")) == "Nothing to download, queue is empty."


def test_start_queue_invalid_type() -> None:
    """Test starting queue with invalid type."""
    test_queue = DownloadQueue()
    assert asyncio.run(test_queue.start_queue("invalid")) == "Invalid queue type."
