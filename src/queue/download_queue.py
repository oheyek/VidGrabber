import asyncio
from src.downloader import Downloader
from src.video_info import VideoInfo
from src.thumbnail_downloader import ThumbnailDownloader
from src.tag_extractor import TagExtractor
from src.logger import log_call

class DownloadQueue:
    def __init__(self) -> None:
        """
        Constructor of a download queue class.
        """
        self.max_downloads: int = 5
        self.videos_queue: dict[str, list[int]] = {}
        self.mp3_queue: list[str] = []
        self.wav_queue: list[str] = []
        self.thumbnail_queue: list[str] = []
        self.tags_queue: list[str] = []
        self.video_info: VideoInfo = VideoInfo()
        self.downloader: Downloader = Downloader(self.video_info)
        self.thumbnail_downloader: ThumbnailDownloader = ThumbnailDownloader(self.video_info)
        self.tag_extractor: TagExtractor = TagExtractor(self.video_info)

    @log_call
    def add_video(self, link: str, quality: int) -> str:
        """
        Method to add videos to queue list.
        :param link: The video link.
        :param quality: Desired video quality.
        :return: Information whether the video has been added to queue or the queue limit has been reached.
        """
        valid_qualities = [144, 240, 360,480,720,1080,1440,2160]

        if not isinstance(link, str) or not link:
            return "Invalid link provided."
        if isinstance(quality, bool) or not isinstance(quality, int):
            return "Incorrect video quality."
        if quality not in valid_qualities:
            return "Incorrect video quality."

        total_videos = sum(len(q) for q in self.videos_queue.values())
        if total_videos >= self.max_downloads:
            return "Queue limit reached."

        if link not in self.videos_queue:
            self.videos_queue[link] = [quality]
        else:
            if quality in self.videos_queue[link]:
                return "Video with this quality already in queue."
            self.videos_queue[link].append(quality)

        return "Video added to queue."