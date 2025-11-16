import pytest

from src.tag_extractor import TagExtractor
from src.video_info import VideoInfo

@pytest.fixture
def tag_extractor() -> TagExtractor:
    """
    Fixture that provides TagExtractor instance for tests.
    :return: TagExtractor instance for tests.
    """
    return TagExtractor(VideoInfo())

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
async def test_extract_tags_valid_links(url: str, tag_extractor) -> None:
    """Test for extracting tags with valid links"""
    result = await tag_extractor.extract_tags(url)
    assert result == "Tags saved to file and copied to clipboard!"

@pytest.mark.asyncio
@pytest.mark.parametrize("url", INVALID_YOUTUBE_URLS)
async def test_extract_tags_invalid_links(url: str, tag_extractor) -> None:
    """Test for extracting tags with invalid links"""
    result = await tag_extractor.extract_tags(url)
    assert result == "Invalid link provided."

@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_input", [None, 123, 12.34])
async def test_extract_tags_invalid_input_types(invalid_input, tag_extractor) -> None:
    """Test for extracting tag with invalid YouTube URLs."""
    result = await tag_extractor.extract_tags(invalid_input)
    assert result == "Invalid link provided."

@pytest.mark.asyncio
async def test_extract_tags_empty_url(tag_extractor) -> None:
    """Test that empty string is rejected while downloading."""
    result = await tag_extractor.extract_tags("")
    assert  result == "Invalid link provided."