import asyncio
from src.downloader import Downloader
from src.video_info import VideoInfo
from src.thumbnail_downloader import ThumbnailDownloader
from src.tag_extractor import TagExtractor


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

    def add_video(self, link: str, quality: int) -> str:
        """
        Method to add videos to a queue list.
        :param link: The video link.
        :param quality: Desired video quality.
        :return: Information whether the video has been added to queue or the queue limit has been reached.
        """
        valid_qualities = [144, 240, 360, 480, 720, 1080, 1440, 2160]

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

        return "Video added to queue"

    def add_mp3_audio(self, link: str) -> str:
        """
        Method to add mp3 audio to a queue list.
        :param link: The video link.
        :return: Information whether the audio has been added to queue or the queue limit has been reached.
        """
        if not isinstance(link, str) or not link:
            return "Invalid link provided."
        if len(self.mp3_queue) >= self.max_downloads:
            return "Queue limit reached."
        self.mp3_queue.append(link)
        return "Audio added to queue"

    def add_wav_audio(self, link: str) -> str:
        """
        Method to add wav audio to a queue list.
        :param link: The video link.
        :return: Information whether the audio has been added to queue or the queue limit has been reached.
        """
        if not isinstance(link, str) or not link:
            return "Invalid link provided."
        if len(self.wav_queue) >= self.max_downloads:
            return "Queue limit reached."
        self.wav_queue.append(link)
        return "Audio added to queue"

    def add_thumbnail(self, link: str) -> str:
        """
        Method to add thumbnails to a queue list.
        :param link: The video link.
        :return: Information whether the thumbnail has been added to queue or the queue limit has been reached.
        """
        if not isinstance(link, str) or not link:
            return "Invalid link provided."
        if len(self.thumbnail_queue) >= self.max_downloads:
            return "Queue limit reached."
        self.thumbnail_queue.append(link)
        return "Thumbnail added to queue"

    def add_tags(self, link: str) -> str:
        """
        Method to add tags to a queue list.
        :param link: The tags link.
        :return: Information whether the tags have been added to queue or the queue limit has been reached.
        """
        if not isinstance(link, str) or not link:
            return "Invalid link provided."
        if len(self.tags_queue) >= self.max_downloads:
            return "Queue limit reached."
        self.tags_queue.append(link)
        return "Tags added to queue"

    async def start_queue(self, queue_type: str) -> str:
        """
        Asynchronous method to start queue with a desired queue type.
        :param queue_type: Type of the files we want to download (MP4, MP3, WAV, JPG or TAGS)
        :return: Success or failure message.
        """
        sem = asyncio.Semaphore(self.max_downloads)

        async def _run_in_thread(func, *args):
            async with sem:
                return await asyncio.to_thread(func, *args)

        if queue_type == "mp4":
            if not self.videos_queue:
                return "Nothing to download, queue is empty."
            tasks = [
                asyncio.create_task(_run_in_thread(self.downloader.download_video, link, quality))
                for link, qualities in self.videos_queue.items()
                for quality in qualities
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for r in results:
                print(r)
            self.videos_queue = {}
            return "All video downloads have been finished."

        elif queue_type == "mp3":
            if not self.mp3_queue:
                return "Nothing to download, queue is empty."
            tasks = [
                asyncio.create_task(_run_in_thread(self.downloader.download_audio, link, "mp3"))
                for link in self.mp3_queue
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for r in results:
                print(r)
            self.mp3_queue = []
            return "All audio downloads have been finished."

        elif queue_type == "wav":
            if not self.wav_queue:
                return "Nothing to download, queue is empty."
            tasks = [
                asyncio.create_task(_run_in_thread(self.downloader.download_audio, link, "wav"))
                for link in self.wav_queue
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for r in results:
                print(r)
            self.wav_queue = []
            return "All audio downloads have been finished."

        elif queue_type == "jpg":
            if not self.thumbnail_queue:
                return "Nothing to download, queue is empty."
            tasks = [
                asyncio.create_task(_run_in_thread(self.thumbnail_downloader.download_thumbnail, link))
                for link in self.thumbnail_queue
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for r in results:
                print(r)
            self.thumbnail_queue = []
            return "All thumbnail downloads have been finished."

        elif queue_type == "csv":
            if not self.tags_queue:
                return "Nothing to download, queue is empty."
            tasks = [
                asyncio.create_task(_run_in_thread(self.tag_extractor.extract_tags, link, False))
                for link in self.tags_queue
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for r in results:
                print(r)
            self.tags_queue = []
            return "All tag extractions have been finished."

        else:
            return "Invalid queue type."
