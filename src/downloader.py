import asyncio
import sys
from pathlib import Path

from .logger import log_call
from .path_manager import PathManager
from .updater import get_ffmpeg_path, get_yt_dlp_path
from .video_info import VideoInfo


class Downloader:
    def __init__(self, video_info: VideoInfo, path_manager: PathManager = None) -> None:
        """
        Initialize Downloader with video info and path management.

        :param video_info: VideoInfo instance for validating and processing video URLs.
        :param path_manager: Optional PathManager instance for managing download paths.
                             If None, creates a new PathManager instance.
        """
        self.video_info = video_info
        self.path_manager = path_manager if path_manager else PathManager()
        self.yt_dlp_path = get_yt_dlp_path()
        self.ffmpeg_path = get_ffmpeg_path()

    @log_call
    async def download_video(self, link: str, quality: int) -> str:
        """
        Download YouTube video in specified quality.

        Supports qualities: 144p, 240p, 360p, 480p, 720p, 1080p, 1440p, 2160p.

        :param link: YouTube video URL (cleaned automatically).
        :param quality: Desired video quality in pixels (e.g., 720, 1080).
        :return: Success message if download completed, error message otherwise.
        """
        if not isinstance(quality, int):
            return "Incorrect video quality."

        allowed_qualities: list[int] = [144, 240, 360, 480, 720, 1080, 1440, 2160, ]

        if quality not in allowed_qualities:
            return "Incorrect video quality."

        link = self.video_info.clean_youtube_url(link)
        if not self.video_info.validator(link) or not link:
            return "Invalid link provided."

        download_path: Path = self.path_manager.get_download_path("mp4")
        output_template: str = str(Path(download_path) / f"%(title)s_{quality}p.%(ext)s")

        try:
            process: asyncio.subprocess.Process = await asyncio.create_subprocess_exec(str(self.yt_dlp_path),
                                                                                       "--format",
                                                                                       f"bestvideo[height={quality}]+bestaudio/best[height={quality}]",
                                                                                       "--merge-output-format",
                                                                                       "mp4", "--ffmpeg-location",
                                                                                       str(self.ffmpeg_path.parent),
                                                                                       "--output", output_template,
                                                                                       "--no-warnings",
                                                                                       "--newline", "--quiet", link,
                                                                                       stdout=asyncio.subprocess.PIPE,
                                                                                       stderr=asyncio.subprocess.PIPE, )

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
        Extract and download audio from YouTube video.

        Supported formats: MP3, WAV (case-insensitive).
        Audio quality is set to 192K bitrate.

        :param link: YouTube video URL (cleaned automatically).
        :param audio_format: Desired audio format ("mp3" or "wav", case-insensitive).
        :return: Success message if download completed, error message otherwise.
        """
        allowed_formats: list[str] = ["MP3", "WAV"]
        audio_format_upper = str(audio_format).strip().upper()

        if audio_format_upper not in allowed_formats:
            return "Incorrect audio format."

        link = self.video_info.clean_youtube_url(link)
        if not self.video_info.validator(link) or not link:
            return "Invalid link provided."

        audio_format_lower: str = audio_format.lower()
        download_path: Path = self.path_manager.get_download_path(audio_format_lower)
        output_template: str = str(Path(download_path) / "%(title)s.%(ext)s")

        try:
            process: asyncio.subprocess.Process = await asyncio.create_subprocess_exec(str(self.yt_dlp_path),
                                                                                       "--format", "bestaudio/best",
                                                                                       "--extract-audio",
                                                                                       "--audio-format",
                                                                                       audio_format_lower,
                                                                                       "--audio-quality", "192K",
                                                                                       "--ffmpeg-location",
                                                                                       str(self.ffmpeg_path.parent),
                                                                                       "--output",
                                                                                       output_template, "--no-warnings",
                                                                                       "--newline", "--quiet", link,
                                                                                       stdout=asyncio.subprocess.PIPE,
                                                                                       stderr=asyncio.subprocess.PIPE, )

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
