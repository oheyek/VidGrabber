import json
import asyncio
from asyncio.subprocess import Process
from pathlib import Path
from typing import List, Optional, Union
from urllib.parse import parse_qs, urlparse

from src.updater import get_yt_dlp_path, get_ffmpeg_path


class VideoInfo:
    ffmpeg_path: Path
    yt_dlp_path: Path

    def __init__(self) -> None:
        """
        Constructor of a VideoInfo class.
        """
        self.yt_dlp_path = get_yt_dlp_path()
        self.ffmpeg_path = get_ffmpeg_path()

    @staticmethod
    def validator(link: str) -> bool:
        """
        Method to validate YouTube link format.
        :param link: The link provided by user.
        :return: Whether the link is a valid YouTube link or not.
        """
        try:
            link: str = link.strip()
            if not link.startswith(("http://", "https://")):
                link = "https://" + link
            return link.startswith(
                (
                    "https://www.youtube.com/watch?v=",
                    "https://youtu.be/",
                    "http://www.youtube.com/watch?v=",
                    "http://youtu.be/",
                )
            )
        except AttributeError:
            return False

    def clean_youtube_url(self, url: str) -> Optional[str]:
        """
        Extract video ID and return clean YouTube URL
        :param url: The link to clean up.
        :return: Cleaned link.
        """
        if not self.validator(url):
            return None
        try:
            url: str = url.strip()
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            parsed = urlparse(url)
            if "youtu.be" in parsed.netloc:
                video_id = parsed.path.lstrip("/")
                return f"https://www.youtube.com/watch?v={video_id}"

            if "youtube.com" in parsed.netloc:
                query_params: dict[str, list[str]] = parse_qs(parsed.query)
                if "v" in query_params:
                    video_id = query_params["v"][0]
                    return f"https://www.youtube.com/watch?v={video_id}"

            return url
        except (AttributeError, TypeError):
            return None

    async def get_video_info(self, link: str) -> Union[str, List[str]]:
        """
        Method to get YouTube video info from a given link.
        :param link: The link provided by user.
        :return: The video information as a list or invalid YouTube link information.
        """
        link = self.clean_youtube_url(link)
        if not self.validator(link) or not link:
            return "Invalid link provided."

        try:
            process: Process = await asyncio.create_subprocess_exec(
                str(self.yt_dlp_path),
                "--dump-json",
                "--no-warnings",
                "--no-playlist",
                "--skip-download",
                "--ffmpeg-location",
                str(self.ffmpeg_path.parent),
                link,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode().strip()
                if "Private video" in error_msg or "unavailable" in error_msg.lower():
                    return (
                        f"Download error (video may be unavailable or private): {link}"
                    )
                return f"Error extracting info: {error_msg}"

            info = json.loads(stdout.decode())

            if not info:
                return f"Could not extract information from: {link}"

            qualities: set[str] = set()
            formats = info.get("formats", [])

            for video_format in formats:
                if (
                    video_format.get("vcodec") != "none"
                    and video_format.get("acodec") != "none"
                ):
                    height = video_format.get("height")
                    fps = video_format.get("fps")
                    ext = video_format.get("ext")

                    if height and fps and ext == "mp4":
                        qualities.add(f"mp4 {height}p {int(fps)}fps")

            qualities_list: list[str] = sorted(
                list(qualities), key=lambda x: int(x.split()[1].rstrip("p"))
            )

            seconds: int = info.get("duration", 0)
            minutes: int = seconds // 60
            remaining: int = seconds % 60

            video_info: list[str] = [
                info.get("title"),
                info.get("uploader"),
                info.get("description"),
                f"{minutes}:{remaining:02d}",
                *qualities_list,
            ]
            return video_info

        except json.JSONDecodeError:
            return f"Error parsing video information: {link}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
