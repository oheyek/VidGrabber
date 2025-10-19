from typing import Optional, List, Union
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
            link = link.strip()
            if not link.startswith(("http://", "https://")):
                link = "https://" + link
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

    def clean_youtube_url(self, url: str) -> Optional[str]:
        """
        Extract video ID and return clean YouTube URL
        :param url: The link to clean up.
        :return: Cleaned link.
        """
        if not self.validator(url):
            return None
        try:
            url = url.strip()
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
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

    def get_video_info(self, link: str) -> Union[str, List[str]]:
        """
        Method to get YouTube video info from a given link.
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
                qualities: list[str] = []
                formats = info.get("formats", [])
                for video_format in formats:
                    if video_format.get("ext") == "mp4":
                        height = video_format.get("height")
                        fps = video_format.get("fps")
                        if height and fps:
                            qualities.append(
                                f"{video_format.get('ext')} {height}p {int(fps)}fps"
                            )

                qualities = list(set(qualities))

                def get_resolution(quality_str: str) -> int:
                    """
                    Function to get a resolution as an int number.
                    :param quality_str: The whole quality string scraped from video.
                    :return: The resolution as an int.
                    """
                    parts = quality_str.split()
                    resolution = parts[1].rstrip("p")
                    return int(resolution)

                qualities = sorted(qualities, key=get_resolution)

                seconds: int = info.get("duration")
                minutes: int = seconds // 60
                remaining: int = seconds % 60

                video_info: list[str] = [
                    info.get("title"),
                    info.get("uploader"),
                    info.get("description"),
                    f"{minutes}:{remaining:02d}",
                    *qualities,
                ]
                return video_info
        except DownloadError:
            return f"Download error (video may be unavailable or private): {link}"
