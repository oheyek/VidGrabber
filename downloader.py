from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


class Downloader:
    def __init__(self, video_info):
        """
        Constructor for downloader class
        """
        self.video_info = video_info
        self.ydl_opts = video_info.ydl_opts

    def download_video(self, link: str, quality: int) -> str:
        """
        Method to download a YouTube video in a desired quality.
        :param link: The link to the video.
        :param quality: The quality user want to download.
        :return: Success message.
        """
        if not isinstance(quality, int):
            return "Incorrect video quality."
        link = self.video_info.clean_youtube_url(link)
        if not self.video_info.validator(link) or not link:
            return "Invalid link provided."
        self.ydl_opts["format"] = f"bestvideo[height={quality}]+bestaudio/best[height={quality}]"
        self.ydl_opts["outtmpl"] = "downloads/%(title)s.%(ext)s"
        self.ydl_opts["merge_output_format"] = "mp4"

        try:
            with YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([link])
                return "Video downloaded"
        except DownloadError:
            return "Incorrect video quality."
