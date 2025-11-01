import sys
from typing import Any
from .path_manager import PathManager
from .logger import log_call

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

path_manager = PathManager()


def progress_hook(download: dict[str, Any]) -> None:
    """
    Hook to display download progress
    :param download: The yt_dlp download process.
    """
    if download["status"] == "downloading":
        percent = download.get("_percent_str", "0%")
        speed = download.get("_speed_str", "N/A")
        sys.stdout.write(f"\rDownloading: {percent} | Speed: {speed}")
        sys.stdout.flush()


class Downloader:
    def __init__(self, video_info) -> None:
        """
        Constructor for downloader class
        """
        self.video_info = video_info
        self.ydl_opts = video_info.ydl_opts

    @log_call
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

        # Get download path and ensure directory exists
        download_path = path_manager.get_download_path("mp4")

        # Create a local copy of options for thread safety
        ydl_opts = self.ydl_opts.copy()
        ydl_opts["format"] = (
            f"bestvideo[height={quality}]+bestaudio/best[height={quality}]"
        )
        ydl_opts["outtmpl"] = {
            "default": f"{download_path}/%(title)s_{quality}p.%(ext)s"
        }
        ydl_opts["merge_output_format"] = "mp4"
        ydl_opts["progress_hooks"] = [progress_hook]

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
                return "Download completed!"
        except DownloadError:
            return "Incorrect video quality."

    @log_call
    def download_audio(self, link: str, audio_format: str) -> str:
        """
        Method to download audio from a YouTube video in a desired format (MP3/WAV).
        :param link: The link to the video
        :param audio_format: The format of the output file user want.
        :return: Success message.
        """
        allowed_formats = ["MP3", "WAV"]
        audio_format_upper = str(audio_format).strip().upper()

        if audio_format_upper not in allowed_formats:
            return "Incorrect audio format."

        link = self.video_info.clean_youtube_url(link)
        if not self.video_info.validator(link) or not link:
            return "Invalid link provided."

        # Get download path and ensure directory exists
        audio_format_lower = audio_format.lower()
        download_path = path_manager.get_download_path(audio_format_lower)

        # Create a local copy of options for thread safety
        ydl_opts = self.ydl_opts.copy()
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["outtmpl"] = {
            "default": f"{download_path}/%(title)s.%(ext)s"
        }
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_format_lower,
                "preferredquality": "192",
            }
        ]
        ydl_opts["progress_hooks"] = [progress_hook]

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
                return f"{audio_format_upper} download completed!"
        except DownloadError as e:
            return f"Download failed: {e}"