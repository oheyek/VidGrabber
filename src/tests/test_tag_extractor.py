import pytest

from src.tag_extractor import TagExtractor
from src.video_info import VideoInfo

video_info = VideoInfo()
tag_extractor = TagExtractor(video_info)

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
def test_extract_tags_valid_links(url: str) -> None:
    """Test for extracting tags with valid links"""
    assert tag_extractor.extract_tags(url) == "Tags saved to file and copied to clipboard!"

@pytest.mark.parametrize("url", INVALID_YOUTUBE_URLS)
def test_extract_tags_invalid_links(url: str) -> None:
    """Test for extracting tags with invalid links"""
    assert tag_extractor.extract_tags(url) == "Invalid link provided."

@pytest.mark.parametrize("invalid_input", [None, 123, [], {}, 12.34])
def test_extract_tags_invalid_input_types(invalid_input) -> None:
    """Test for extracting tag with invalid YouTube URLs."""
    assert tag_extractor.extract_tags(invalid_input) == "Invalid link provided."

def test_extract_tags_empty_url() -> None:
    """Test that empty string is rejected while downloading."""
    assert tag_extractor.extract_tags("") == "Invalid link provided."