import os

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


def save_tags(tags: list[str], title: str) -> None:
    """
    Function to save tags to a csv file.
    :param tags: The list of tags downloaded from YouTube video.
    :param title: The title of the video.
    """
    os.makedirs("downloads/tags", exist_ok=True)
    with open(f"downloads/tags/{title}_tags.csv", "w", newline="", encoding="utf-8") as f:
        for tag in tags:
            f.write(f"{tag},\n")


class TagExtractor:
    def __init__(self, video_info) -> None:
        """
        Constructor for a tag extractor class
        """
        self.video_info = video_info
        self.ydl_opts = video_info.ydl_opts


    def extract_tags(self, link: str) -> str:
        """
        Method to extract tags list from a YouTube video link.
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
            save_tags(tags, title)
            return "Tags saved to file!"
        except DownloadError as e:
            return f"Download failed: {e}"

