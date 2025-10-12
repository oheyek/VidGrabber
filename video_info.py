from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


class VideoInfo:
    def __init__(self) -> None:
        """
        Constructor of a VideoInfo class.
        """
        self.ydl_opts: dict = {'quiet': True, 'no_warnings': True, 'extract_flat': False,
                               'force_generic_extractor': False}

    @staticmethod
    def validator(link: str) -> bool:
        """
        Function to validate YouTube link format.
        :param link: The link provided by user.
        :return: Whether the link is a valid YouTube link or not.
        """
        return link.startswith(
            ("https://www.youtube.com/watch?v=", "https://youtu.be/", "http://www.youtube.com/watch?v=",
             "http://youtu.be/",))

    def get_video_info(self, link: str) -> str | list:
        """
        Method to get YouTube video title from a given link.
        :param link: The provided by user.
        :return: The video information as a list or invalid YouTube link information.
        """
        if not self.validator(link):
            return "Invalid YouTube link."
        try:
            with YoutubeDL(self.ydl_opts) as ydl:
                info: dict = ydl.extract_info(link, download=False)

                if not info:
                    return f"Could not extract information from: {link}"

                seconds: int = info.get("duration")
                minutes: int = seconds // 60
                remaining: int = seconds % 60
                video_info: list = [info.get("title"), info.get("uploader"), info.get("description"),
                                    f"{minutes}:{remaining}", ]
                return video_info
        except DownloadError:
            return f"Download error (video may be unavailable or private): {link}"
