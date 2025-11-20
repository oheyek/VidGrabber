import asyncio
import sys
from pathlib import Path

from .logger import log_call
from .path_manager import PathManager
from .updater import get_yt_dlp_path, get_ffmpeg_path
from .video_info import VideoInfo


class ThumbnailDownloader:
    def __init__(self, video_info: VideoInfo, path_manager: PathManager = None) -> None:
        """
        Initialize ThumbnailDownloader with video info and path manager instances.
        :param video_info: VideoInfo instance for link validation and cleaning.
        :param path_manager: PathManager instance for handling download paths, creates new if None.
        """
        self.video_info = video_info
        self.path_manager = path_manager if path_manager else PathManager()
        self.yt_dlp_path = get_yt_dlp_path()
        self.ffmpeg_path = get_ffmpeg_path()

    @log_call
    async def download_thumbnail(self, link: str) -> str:
        """
        Download thumbnail image from YouTube video and convert to JPG format.
        :param link: YouTube video link from which to download thumbnail.
        :return: Success message if download completed or error message if download failed.
        """
        link = self.video_info.clean_youtube_url(link)
        if not self.video_info.validator(link) or not link:
            return "Invalid link provided."

        output_path: Path = self.path_manager.get_download_path('jpg')
        output_template: str = str(output_path / "%(title)s.%(ext)s")

        try:
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = 0x08000000

            process: asyncio.subprocess.Process = await asyncio.create_subprocess_exec(str(self.yt_dlp_path),
                                                                                       "--skip-download",
                                                                                       "--write-thumbnail",
                                                                                       "--convert-thumbnails", "jpg",
                                                                                       "--ffmpeg-location",
                                                                                       str(self.ffmpeg_path.parent),
                                                                                       "--output", output_template,
                                                                                       "--no-warnings", link,
                                                                                       stdout=asyncio.subprocess.PIPE,
                                                                                       stderr=asyncio.subprocess.PIPE,
                                                                                       creationflags=creation_flags)

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode("utf-8", errors="replace").strip()
                return f"Download failed: {error_msg}"

            return "Thumbnail download completed!"

        except Exception as e:
            return f"Download failed: {str(e)}"
