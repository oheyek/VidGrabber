import asyncio
import sys
from pathlib import Path
from typing import Any

from .path_manager import PathManager
from .logger import log_call
from .updater import get_ffmpeg_path, get_yt_dlp_path

path_manager = PathManager()

class Downloader:
    def __init__(self, video_info) -> None:
        """
        Constructor of a downloader class.
        """
        self.video_info = video_info
        self.yt_dlp_path = get_yt_dlp_path()
        self.ffmpeg_path = get_ffmpeg_path()

    @log_call
    async def download_video(self, link: str, quality: int) -> str:
        """
        Method to download a YouTube video in a desired quality.
        :param link: The link to the video.
        :param quality: The quality user want to download.
        :return: Success message.
        """
        if not isinstance(quality, int):
            return "Incorrect video quality"

        link = self.video_info.clean_youtube_url(link)
        if not self.video_info.validator(link) or not link:
            return "Invalid link provided."

        download_path = path_manager.get_download_path("mp4")
        output_template = str(Path(download_path) / f"%(title)s_{quality}p.%(ext)s")

        try:
            process = await asyncio.create_subprocess_exec(
                str(self.yt_dlp_path),
                "--format", f"bestvideo[height={quality}]+bestaudio/best[height={quality}]",
                "--merge-output-format", "mp4",
                "--fmpeg-location", str(self.ffmpeg_path.parent),
                "--output", output_template,
                "--no-warning",
                "--newline",
                link,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                output = line.decode().strip()
                if output:
                    sys.stdout.write(f"\r{output}")
                    sys.stdout.flush()

            await process.wait()

            if process.returncode != 0:
                stderr = await process.stderr.read()
                error_msg = stderr.decode().strip()
                return f"Download failed: {error_msg or 'Incorrect video quality'}"

            return "Download completed!"

        except Exception as e:
            return f"Download failed: {str(e)}"