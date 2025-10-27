import os

import pyperclip
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from .path_manager import PathManager
path_manager: PathManager = PathManager()
paths = path_manager.load_settings()

def save_tags_and_copy_to_clipboard(tags: list[str], title: str, copy: bool) -> None:
    """
    Function to save tags to a csv file and copy them to a clipboard.
    :param copy: Bool value whether the tags have to be copied to clipboard.
    :param tags: The list of tags downloaded from YouTube video.
    :param title: The title of the video.
    """
    os.makedirs(paths.get("tags"), exist_ok=True)
    tags_text = "".join(f"{tag},\n" for tag in tags)
    with open(f"{paths.get("tags")}/{title}_tags.csv", "w", newline="", encoding="utf-8") as f:
        f.write(tags_text)
    if copy:
        try:
            pyperclip.copy(tags_text)
            return "Tags saved to file and copied to clipboard!"
        except Exception as e:
            return f"Tags saved to file only (no clipboard access) {e}"
    return "Tags saved to file."


class TagExtractor:
    def __init__(self, video_info) -> None:
        """
        Constructor for a tag extractor class
        """
        self.video_info = video_info
        self.ydl_opts = video_info.ydl_opts


    def extract_tags(self, link: str, copy: bool = True) -> str:
        """
        Method to extract tags list from a YouTube video link.
        :param copy: Bool value whether the tags have to be copied to clipboard.
        :param link: The YouTube video.
        :return: Success message.
        """
        link = self.video_info.clean_youtube_url(link)
        if not self.video_info.validator(link) or not link:
            return "Invalid link provided."
        self.ydl_opts["skip_download"] = True
        try:
            with YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
            tags = info.get("tags") or []
            title = (info.get("title") or "").replace(" ", "_")
            return save_tags_and_copy_to_clipboard(tags, title, copy)
        except DownloadError as e:
            return f"Download failed: {e}"

