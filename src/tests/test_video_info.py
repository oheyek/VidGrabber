import pytest

from src.video_info import VideoInfo


@pytest.fixture
def video_info() -> VideoInfo:
    """
    Fixture that provides VideInfo instance for tests.
    :return: VideoInfo instance for tests.
    """
    return VideoInfo()

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


@pytest.mark.parametrize("url", VALID_YOUTUBE_URLS)
def test_valid_youtube_urls(url: str, video_info) -> None:
    """Test that valid YouTube URLs are accepted."""
    assert video_info.validator(url)


@pytest.mark.parametrize("url", INVALID_YOUTUBE_URLS)
def test_invalid_youtube_urls(url: str, video_info) -> None:
    """Test that invalid YouTube URLs are rejected."""
    assert not video_info.validator(url)


@pytest.mark.parametrize("invalid_input", [None, 123, 12.34])
def test_invalid_input_types(invalid_input, video_info) -> None:
    """Test that non-string inputs return error message."""
    assert not video_info.validator(invalid_input)


def test_empty_string(video_info) -> None:
    """Test that empty string is rejected."""
    assert not video_info.validator("")


@pytest.mark.parametrize("url", VALID_YOUTUBE_URLS)
def test_clean_valid_urls(url: str, video_info) -> None:
    """Test for cleaning valid YouTube URLs."""
    assert (
        video_info.clean_youtube_url(url)
        == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    )


@pytest.mark.parametrize("url", INVALID_YOUTUBE_URLS)
def test_clean_invalid_urls(url: str, video_info) -> None:
    """Test for checking whether cleaning invalid YouTube URLs is rejected."""
    assert video_info.clean_youtube_url(url) is None


@pytest.mark.parametrize("invalid_input", [None, 123, 12.34])
def test_clean_invalid_input_types(invalid_input, video_info) -> None:
    """Test that non-string inputs return error message."""
    assert video_info.clean_youtube_url(invalid_input) is None


def test_cleaning_empty_string(video_info) -> None:
    """Test that empty string is rejected."""
    assert not video_info.validator("") == "Invalid link provided."


@pytest.mark.asyncio
@pytest.mark.parametrize("url", VALID_YOUTUBE_URLS)
async def test_get_info_valid_urls(url: str, video_info) -> None:
    """Test for getting info of a valid YouTube URLs."""
    result = await video_info.get_video_info(url)

    assert isinstance(result, list)

    assert (
        result[0]
        == "Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)"
    )
    assert result[1] == "Rick Astley"
    assert "Never Gonna Give You Up" in result[2]
    assert result[3] == "3:33"

    qualities = result[4:]
    assert "mp4 144p 25fps" in qualities
    assert "mp4 360p 25fps" in qualities
    assert "mp4 720p 25fps" in qualities
    assert "mp4 1080p 25fps" in qualities

    for quality in qualities:
        assert quality.startswith("mp4")
        assert "fps" in quality


@pytest.mark.asyncio
@pytest.mark.parametrize("url", INVALID_YOUTUBE_URLS)
async def test_get_info_invalid_urls(url: str, video_info) -> None:
    """Test for getting info of an invalid YouTube URLs."""
    result = await video_info.get_video_info(url)
    assert result == "Invalid link provided."


@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_input", [None, 123, 12.34])
async def test_get_info_invalid_input_types(invalid_input, video_info) -> None:
    """Test that non-string inputs return error message."""
    result = await video_info.get_video_info(invalid_input)
    assert result == "Invalid link provided."


@pytest.mark.asyncio
async def test_video_unavailable(video_info) -> None:
    """Test for the video that is unavailable or private."""
    link = "https://youtu.be/test123"
    result = await video_info.get_video_info(link)
    assert result.startswith("Error extracting info:") or result.startswith("Download error")



@pytest.mark.asyncio
async def test_get_info_empty_string(video_info) -> None:
    """Test that empty string is rejected."""
    result = await video_info.get_video_info("")
    assert result == "Invalid link provided."
