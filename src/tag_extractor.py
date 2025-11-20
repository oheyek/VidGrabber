import asyncio
import json
import sys
from pathlib import Path
from typing import Any, LiteralString

import pyperclip

from .logger import log_call
from .path_manager import PathManager
from .updater import get_ffmpeg_path, get_yt_dlp_path
from .video_info import VideoInfo


def sanitize_filename(filename: str) -> str:
    """
    Remove or replace characters that are invalid in file names.
    :param filename: Original filename to be sanitized.
    :return: Sanitized filename safe for file system operations.
    """
    # Characters forbidden in Windows filenames
    invalid_chars = '<>:"/\\|?*'

    # Replace invalid chars with underscore
    for char in invalid_chars:
        filename = filename.replace(char, "_")

    # Remove/replace problematic Unicode characters
    filename = filename.encode('ascii', errors='ignore').decode('ascii')

    # Remove leading/trailing spaces and dots
    filename = filename.strip(". ")

    # Replace multiple underscores with single one
    while "__" in filename:
        filename = filename.replace("__", "_")

    # Limit filename length
    if len(filename) > 200:
        filename = filename[:200]

    return filename or "video"


def save_tags_and_copy_to_clipboard(tags: list[str], title: str, copy: bool, path_manager: PathManager) -> str:
    """
    Save tags to a CSV file and optionally copy them to clipboard.
    :param tags: The list of tags downloaded from YouTube video.
    :param title: The title of the video.
    :param copy: Bool value whether the tags have to be copied to clipboard.
    :param path_manager: The path manager instance for extracting download path.
    :return: Status message indicating success or failure of the operation.
    """
    output_path: Path = path_manager.get_download_path("tags")
    output_path.mkdir(parents=True, exist_ok=True)

    safe_title = sanitize_filename(title.replace(" ", "_"))
    tags_text: str = "".join(f"{tag},\n" for tag in tags)

    try:
        with open(output_path / f"{safe_title}_tags.csv", "w", newline="", encoding="utf-8") as f:
            f.write(tags_text)
    except OSError as e:
        return f"Failed to save tags: {str(e)}"

    if copy:
        try:
            pyperclip.copy(tags_text)
            return "Tags saved to file and copied to clipboard!"
        except Exception as e:
            return f"Tags saved to file only (no clipboard access) {e}"
    return "Tags saved to file"


class TagExtractor:
    def __init__(self, video_info: VideoInfo, path_manager: PathManager = None) -> None:
        """
        Initialize TagExtractor with video info and path manager instances.
        :param video_info: VideoInfo instance for link validation and cleaning.
        :param path_manager: PathManager instance for handling download paths, creates new if None.
        """
        self.video_info = video_info
        self.path_manager = path_manager if path_manager else PathManager()
        self.yt_dlp_path = get_yt_dlp_path()
        self.ffmpeg_path = get_ffmpeg_path()

    @log_call
    async def extract_tags(self, link: str, copy: bool = True) -> str:
        """
        Extract tags list from a YouTube video link and save to file.
        :param link: The YouTube video link from which to extract tags.
        :param copy: Bool value whether the tags have to be copied to clipboard.
        :return: Success message if extraction completed or error message if extraction failed.
        """
        link = self.video_info.clean_youtube_url(link)
        if not self.video_info.validator(link) or not link:
            return "Invalid link provided."

        try:
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = 0x08000000
            process: asyncio.subprocess.Process = await asyncio.create_subprocess_exec(str(self.yt_dlp_path),
                                                                                       "--dump-json", "--no-warnings",
                                                                                       "--skip-download",
                                                                                       "--ffmpeg-location",
                                                                                       str(self.ffmpeg_path.parent),
                                                                                       link,
                                                                                       stdout=asyncio.subprocess.PIPE,
                                                                                       stderr=asyncio.subprocess.PIPE,
                                                                                       creationflags=creation_flags)

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='replace').strip()
                return f"Download failed: {error_msg}"

            info = json.loads(stdout.decode('utf-8', errors='replace'))
            tags: list[Any] | Any = info.get("tags") or []
            title: LiteralString = (info.get("title") or "").replace(" ", "_")

            return save_tags_and_copy_to_clipboard(tags, title, copy, self.path_manager)

        except json.JSONDecodeError:
            return f"Error parsing video information: {link}"
        except Exception as e:
            return f"Download failed: {str(e)}"
