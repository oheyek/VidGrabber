from yt_dlp import YoutubeDL


class VideoInfo:
    def __init__(self) -> None:
        """
        Constructor of a VideoInfo class.
        """
        self.ydl_opts: dict = {"quiet": True, "skip_download": True, }

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
        :return: The video information as a list or invalid youtube link information.
        """
        if self.validator(link):
            with YoutubeDL(self.ydl_opts) as ydl:
                info: dict = ydl.extract_info(link, download=False)
                seconds: int = info.get("duration")
                minutes: int = seconds // 60
                remaining: int = seconds % 60
                video_info: list = [info.get("title"), info.get("uploader"), info.get("description"),
                    f"{minutes}:{remaining}", ]
                return video_info

        return "Invalid youtube link."
