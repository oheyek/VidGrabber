from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from .path_manager import PathManager
from .logger import log_call

path_manager: PathManager = PathManager()
paths = path_manager.load_settings() or {}


class ThumbnailDownloader:
    def __init__(self, video_info) -> None:
        """
        Constructor for a thumbnail downloader class
        """
        self.video_info = video_info
        self.ydl_opts = video_info.ydl_opts

    @log_call
    def download_thumbnail(self, link: str) -> str:
        """
        Method to download a thumbnail from a YouTube video link.
        :param link: YouTube video link.
        :return: Success or failure message.
        """
        link = self.video_info.clean_youtube_url(link)
        if not self.video_info.validator(link) or not link:
            return "Invalid link provided."
        self.ydl_opts["skip_download"] = True
        self.ydl_opts["writethumbnail"] = True
        self.ydl_opts["outtmpl"] = f"{paths.get('jpg')}/%(title)s.%(ext)s"
        self.ydl_opts["postprocessors"] = [
            {"format": "jpg", "key": "FFmpegThumbnailsConvertor", "when": "before_dl"}
        ]

        try:
            with YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([link])
                return "Thumbnail download completed!"
        except DownloadError as e:
            return f"Download failed: {e}"
