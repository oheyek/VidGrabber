import asyncio
import sys
from pathlib import Path

from .path_manager import PathManager
from .logger import log_call
from .updater import get_ffmpeg_path, get_yt_dlp_path

path_manager: PathManager = PathManager()


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
            return "Incorrect video quality."

        allowed_qualities: list[int] = [
            144,
            240,
            360,
            480,
            720,
            1080,
            1440,
            2160,
        ]

        if quality not in allowed_qualities:
            return "Incorrect video quality."

        link = self.video_info.clean_youtube_url(link)
        if not self.video_info.validator(link) or not link:
            return "Invalid link provided."

        download_path: Path = path_manager.get_download_path("mp4")
        output_template: str = str(
            Path(download_path) / f"%(title)s_{quality}p.%(ext)s"
        )

        try:
            process: asyncio.subprocess.Process = await asyncio.create_subprocess_exec(
                str(self.yt_dlp_path),
                "--format",
                f"bestvideo[height={quality}]+bestaudio/best[height={quality}]",
                "--merge-output-format",
                "mp4",
                "--ffmpeg-location",
                str(self.ffmpeg_path.parent),
                "--output",
                output_template,
                "--no-warnings",
                "--newline",
                "--quiet",
                link,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                output: str = line.decode("utf-8", errors="replace").strip()
                if output:
                    sys.stdout.write(f"\r{output}")
                    sys.stdout.flush()

            await process.wait()

            if process.returncode != 0:
                stderr = await process.stderr.read()
                error_msg = stderr.decode("utf-8", errors="replace").strip()
                return f"Download failed: {error_msg or 'Incorrect video quality'}"

            return "Download completed!"

        except Exception as e:
            return f"Download failed: {str(e)}"

    @log_call
    async def download_audio(self, link: str, audio_format: str) -> str:
        """
        Method to download audio from a YouTube video in a desired format (MP3/WAV).
        :param link: The link to the video.
        :param audio_format: The format of the output file user want.
        :return: Success message.
        """
        allowed_formats: list[str] = ["MP3", "WAV"]
        audio_format_upper = str(audio_format).strip().upper()

        if audio_format_upper not in allowed_formats:
            return "Incorrect audio format."

        link = self.video_info.clean_youtube_url(link)
        if not self.video_info.validator(link) or not link:
            return "Invalid link provided."

        audio_format_lower: str = audio_format.lower()
        download_path: Path = path_manager.get_download_path(audio_format_lower)
        output_template: str = str(Path(download_path) / "%(title)s.%(ext)s")

        try:
            process: asyncio.subprocess.Process = await asyncio.create_subprocess_exec(
                str(self.yt_dlp_path),
                "--format",
                "bestaudio/best",
                "--extract-audio",
                "--audio-format",
                audio_format_lower,
                "--audio-quality",
                "192K",
                "--ffmpeg-location",
                str(self.ffmpeg_path.parent),
                "--output",
                output_template,
                "--no-warnings",
                "--newline",
                "--quiet",
                link,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                output = line.decode("utf-8", errors="replace").strip()
                if output:
                    sys.stdout.write(f"\r{output}")
                    sys.stdout.flush()

            await process.wait()

            if process.returncode != 0:
                stderr = await process.stderr.read()
                error_msg = stderr.decode("utf-8", errors="replace").strip()
                return f"Download failed: {error_msg}"

            return f"{audio_format_upper} download completed!"

        except Exception as e:
            return f"Download failed: {str(e)}"
