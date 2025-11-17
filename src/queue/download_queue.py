import asyncio
from dataclasses import dataclass

from src.downloader import Downloader
from src.logger import log_call
from src.tag_extractor import TagExtractor
from src.thumbnail_downloader import ThumbnailDownloader
from src.video_info import VideoInfo


@dataclass
class QueueItem:
    link: str
    title: str


class DownloadQueue:
    def __init__(self) -> None:
        """
        Constructor of a download queue class.
        """
        self.max_downloads: int = 5
        self.videos_queue: dict[str, list[tuple[int, str]]] = {}  # {link: [(quality, title)]}
        self.mp3_queue: list[QueueItem] = []
        self.wav_queue: list[QueueItem] = []
        self.thumbnail_queue: list[QueueItem] = []
        self.tags_queue: list[QueueItem] = []
        self.video_info: VideoInfo = VideoInfo()
        self.downloader: Downloader = Downloader(self.video_info)
        self.thumbnail_downloader: ThumbnailDownloader = ThumbnailDownloader(self.video_info)
        self.tag_extractor: TagExtractor = TagExtractor(self.video_info)

    @log_call
    async def add_video(self, link: str, quality: int, title: str) -> str:
        """
        Method to add videos to queue list.
        :param link: The video link.
        :param quality: Desired video quality.
        :param title: Video title.
        :return: Information whether the video has been added to queue or the queue limit has been reached.
        """
        valid_qualities: list[int] = [144, 240, 360, 480, 720, 1080, 1440, 2160]

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
            self.videos_queue[link] = [(quality, title)]
        else:
            if any(q[0] == quality for q in self.videos_queue[link]):
                return "Video with this quality already in queue."
            self.videos_queue[link].append((quality, title))

        return "Video added to queue."

    @log_call
    async def add_mp3_audio(self, link: str, title: str) -> str:
        """
        Method to add mp3 audio to queue list.
        :param link: The video link.
        :param title: Video title.
        :return: Information whether the audio has been added to queue or the queue limit has been reached.
        """
        if not isinstance(link, str) or not link:
            return "Invalid link provided."
        if any(item.link == link for item in self.mp3_queue):
            return "Audio already in queue."
        if len(self.mp3_queue) >= self.max_downloads:
            return "Queue limit reached."
        self.mp3_queue.append(QueueItem(link, title))
        return "Audio added to queue."

    @log_call
    async def add_wav_audio(self, link: str, title: str) -> str:
        """
        Method to add wav audio to queue list.
        :param link: The video link.
        :param title: Video title.
        :return: Information whether the audio has been added to queue or the queue limit has been reached.
        """
        if not isinstance(link, str) or not link:
            return "Invalid link provided."
        if any(item.link == link for item in self.wav_queue):
            return "Audio already in queue."
        if len(self.wav_queue) >= self.max_downloads:
            return "Queue limit reached."
        self.wav_queue.append(QueueItem(link, title))
        return "Audio added to queue."

    @log_call
    async def add_thumbnail(self, link: str, title: str) -> str:
        """
        Method to add thumbnails to a queue list.
        :param link: The video link.
        :param title: Video title.
        :return: Information whether the thumbnail has been added to queue or the queue limit has been reached.
        """
        if not isinstance(link, str) or not link:
            return "Invalid link provided."
        if any(item.link == link for item in self.thumbnail_queue):
            return "Thumbnail already in queue."
        if len(self.thumbnail_queue) >= self.max_downloads:
            return "Queue limit reached."
        self.thumbnail_queue.append(QueueItem(link, title))
        return "Thumbnail added to queue"

    @log_call
    async def add_tags(self, link: str, title: str) -> str:
        """
        Method to add tags to a queue list.
        :param link: The tags link.
        :param title: Video title.
        :return: Information whether the tags have been added to queue or the queue limit has been reached.
        """
        if not isinstance(link, str) or not link:
            return "Invalid link provided."
        if any(item.link == link for item in self.tags_queue):
            return "Tags already in queue."
        if len(self.tags_queue) >= self.max_downloads:
            return "Queue limit reached."
        self.tags_queue.append(QueueItem(link, title))
        return "Tags added to queue"

    @log_call
    async def start_queue(self, queue_type: str) -> str:
        """
        Asynchronous method to start queue with a desired queue type.
        :param queue_type: Type of the files we want to download (MP4, MP3, WAV, JPG or TAGS)
        :return: Success or failure message.
        """
        sem: asyncio.Semaphore = asyncio.Semaphore(self.max_downloads)

        async def _run_with_semaphore(coro):
            async with sem:
                return await coro

        if queue_type == "mp4":
            if not self.videos_queue:
                return "Nothing to download, queue is empty."
            tasks: list = []
            for link, qualities in self.videos_queue.items():
                for quality_tuple in qualities:
                    quality = quality_tuple[0]
                    tasks.append(
                        asyncio.create_task(
                            _run_with_semaphore(self.downloader.download_video(link, quality))
                        )
                    )
            results = await asyncio.gather(*tasks, return_exceptions=True)
            self.videos_queue = {}
            return "All video downloads have been finished."

        elif queue_type == "mp3":
            if not self.mp3_queue:
                return "Nothing to download, queue is empty."
            tasks = [
                asyncio.create_task(
                    _run_with_semaphore(self.downloader.download_audio(item.link, "mp3"))
                )
                for item in self.mp3_queue
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            self.mp3_queue = []
            return "All audio downloads have been finished."

        elif queue_type == "wav":
            if not self.wav_queue:
                return "Nothing to download, queue is empty."
            tasks = [
                asyncio.create_task(
                    _run_with_semaphore(self.downloader.download_audio(item.link, "wav"))
                )
                for item in self.wav_queue
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            self.wav_queue = []
            return "All audio downloads have been finished."

        elif queue_type == "jpg":
            if not self.thumbnail_queue:
                return "Nothing to download, queue is empty."
            tasks = [
                asyncio.create_task(
                    _run_with_semaphore(self.thumbnail_downloader.download_thumbnail(item.link))
                )
                for item in self.thumbnail_queue
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            self.thumbnail_queue = []
            return "All thumbnail downloads have been finished."

        elif queue_type == "csv":
            if not self.tags_queue:
                return "Nothing to download, queue is empty."
            tasks = [
                asyncio.create_task(
                    _run_with_semaphore(self.tag_extractor.extract_tags(item.link, False))
                )
                for item in self.tags_queue
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            self.tags_queue = []
            return "All tag extractions have been finished."

        else:
            return "Invalid queue type."