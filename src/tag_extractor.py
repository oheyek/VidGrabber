import asyncio
import json
from pathlib import Path

import pyperclip

from .path_manager import PathManager
from .logger import log_call
from .updater import get_ffmpeg_path, get_yt_dlp_path

path_manager: PathManager = PathManager()
paths = path_manager.load_settings() or {}

def save_tags_and_copy_to_clipboard(tags: list[str], title: str, copy: bool) -> str:
    """
    Function to save tags to a csv file and copy them to a clipboard.
    :param copy: Bool value whether the tags have to be copied to clipboard.
    :param tags: The list of tags downloaded from YouTube video.
    :param title: The title of the video.
    """
    output_path = Path(paths.get("tags", "."))
    output_path.mkdir(parents=True, exist_ok=True)

    tags_text = "".join(f"{tag},\n" for tag in tags)

    with open(output_path / f"{title}_tags.csv", "w", newline="", encoding="utf-8") as f:
        f.write(tags_text)

    if copy:
        try:
            pyperclip.copy(tags_text)
            return "Tags saved to file and copied to clipboard!"
        except Exception as e:
            return f"Tags saved to file only (no clipboard access) {e}"
    return "Tags saved to file"

class TagExtractor:
    def __init__(self, video_info) -> None:
        """
        Constructor for a tag extractor class.
        """
        self.video_info = video_info
        self.yt_dlp_path = get_yt_dlp_path()
        self.ffmpeg_path = get_ffmpeg_path()

    @log_call
    async def extract_tags(self, link: str, copy: bool = True) -> str:
        """
        Method to extract tags list from a YouTube video link.
        :param link: The YouTube video.
        :param copy: Bool value whether the tags have to be copied to clipboard.
        :return: Success message.
        """
        link = self.video_info.clean_youtube_url(link)
        if not self.video_info.validator(link) or not link:
            return "Invalid link provided."

        try:
            process = await  asyncio.create_subprocess_exec(
                str(self.yt_dlp_path),
                "--dump-json",
                "--no-warnings",
                "--skip-download",
                "--ffmpeg-location", str(self.ffmpeg_path.parent),
                link,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode().strip()
                return f"Download failed: {error_msg}"
            info = json.loads(stdout.decode())
            tags = info.get("tags") or []
            title = (info.get("title") or "").replace(" ","_")

            return save_tags_and_copy_to_clipboard(tags, title, copy)

        except json.JSONDecodeError:
            return f"Error parsing video information: {link}"
        except Exception as e:
            return f"Download failed: {str(e)}"
