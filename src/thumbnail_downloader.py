import asyncio
from pathlib import Path

from .path_manager import PathManager
from .logger import log_call
from .updater import get_yt_dlp_path, get_ffmpeg_path
from .video_info import VideoInfo

class ThumbnailDownloader:
    def __init__(self, video_info: VideoInfo, path_manager: PathManager = None) -> None:
        """
        Constructor for a thumbnail downloader class.
        """
        self.video_info = video_info
        self.path_manager = path_manager if path_manager else PathManager()
        self.yt_dlp_path = get_yt_dlp_path()
        self.ffmpeg_path = get_ffmpeg_path()

    @log_call
    async def download_thumbnail(self, link: str) -> str:
        """
        Method to download a thumbnail from a YouTube video link.
        :param link: YouTube video link.
        :return: Success or failure message.
        """
        link = self.video_info.clean_youtube_url(link)
        if not self.video_info.validator(link) or not link:
            return "Invalid link provided."

        output_path: Path = self.path_manager.get_download_path('jpg')
        output_template: str = str(output_path / "%(title)s.%(ext)s")

        try:
            process: asyncio.subprocess.Process = await asyncio.create_subprocess_exec(
                str(self.yt_dlp_path),
                "--skip-download",
                "--write-thumbnail",
                "--convert-thumbnails", "jpg",
                "--ffmpeg-location", str(self.ffmpeg_path.parent),
                "--output", output_template,
                "--no-warnings",
                link,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode("utf-8", errors="replace").strip()
                return f"Download failed: {error_msg}"

            return "Thumbnail download completed!"

        except Exception as e:
            return f"Download failed: {str(e)}"
