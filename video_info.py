from urllib.parse import urlparse, parse_qs

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


class VideoInfo:
    def __init__(self) -> None:
        """
        Constructor of a VideoInfo class.
        """
        self.ydl_opts: dict[str, bool] = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "force_generic_extractor": False,
            "noplaylist": True,
        }

    @staticmethod
    def validator(link: str) -> bool:
        """
        Method to validate YouTube link format.
        :param link: The link provided by user.
        :return: Whether the link is a valid YouTube link or not.
        """
        try:
            return link.startswith(
                (
                    "https://www.youtube.com/watch?v=",
                    "https://youtu.be/",
                    "http://www.youtube.com/watch?v=",
                    "http://youtu.be/",
                )
            )
        except AttributeError:
            return False

    def clean_youtube_url(self, url: str) -> str | None:
        """
        Extract video ID and return clean YouTube URL
        :param url: The link to clean up.
        :return: Cleaned link.
        """
        if not self.validator(url):
            return None
        try:
            parsed = urlparse(url)
            if "youtu.be" in parsed.netloc:
                video_id = parsed.path.lstrip("/")
                return f"https://www.youtube.com/watch?v={video_id}"

            if "youtube.com" in parsed.netloc:
                query_params: dict[str, list[str]] = parse_qs(parsed.query)
                if "v" in query_params:
                    video_id = query_params["v"][0]
                    return f"https://www.youtube.com/watch?v={video_id}"

            return url
        except (AttributeError, TypeError):
            return None

    def get_video_info(self, link: str) -> str | list[str]:
        """
        Method to get YouTube video title from a given link.
        :param link: The link provided by user.
        :return: The video information as a list or invalid YouTube link information.
        """
        link = self.clean_youtube_url(link)
        if not self.validator(link) or not link:
            return "Invalid link provided."
        try:
            with YoutubeDL(self.ydl_opts) as ydl:
                info: dict = ydl.extract_info(link, download=False)
                if not info:
                    return f"Could not extract information from: {link}"

                seconds: int = info.get("duration")
                minutes: int = seconds // 60
                remaining: int = seconds % 60
                video_info: list = [
                    info.get("title"),
                    info.get("uploader"),
                    info.get("description"),
                    f"{minutes}:{remaining}",
                ]
                return video_info
        except DownloadError:
            return f"Download error (video may be unavailable or private): {link}"
