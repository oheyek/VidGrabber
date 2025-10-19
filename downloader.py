import sys
from typing import Any

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


def progress_hook(download: dict[str, Any]) -> None:
    """
    Hook to display download progress
    :param download: The yt_dlp download process.
    :return:
    """
    if download["status"] == "downloading":
        percent = download.get("_percent_str", "0%")
        speed = download.get("_speed_str", "N/A")

        sys.stdout.write(f"\rDownloading: {percent} | Speed: {speed}")
        sys.stdout.flush()

    elif download["status"] == "finished":
        return


class Downloader:
    def __init__(self, video_info) -> None:
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
        self.ydl_opts["format"] = (
            f"bestvideo[height={quality}]+bestaudio/best[height={quality}]"
        )
        self.ydl_opts["outtmpl"] = "downloads/mp4/%(title)s.%(ext)s"
        self.ydl_opts["merge_output_format"] = "mp4"
        self.ydl_opts["progress_hooks"] = [progress_hook]

        try:
            with YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([link])
                return "Download completed!"
        except DownloadError:
            return "Incorrect video quality."

    def download_mp3(self, link: str) -> str:
        link = self.video_info.clean_youtube_url(link)
        if not self.video_info.validator(link) or not link:
            return "Invalid link provided."
        self.ydl_opts["format"] = "bestaudio/best"
        self.ydl_opts["outtmpl"] = "downloads/mp3/%(title)s.%(ext)s"
        self.ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]
        self.ydl_opts["progress_hooks"] = [progress_hook]

        try:
            with YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([link])
                return "MP3 download completed!"
        except DownloadError as e:
            return "Incorrect video."
