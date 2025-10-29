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
        self.videos_queue:dict[str, int] = {}
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
        if not isinstance(quality, int) or isinstance(quality, bool):
            return "Incorrect video quality."
        if quality not in valid_qualities:
            return "Incorrect video quality."
        if len(self.videos_queue) >= self.max_downloads:
            return "Queue limit reached."
        self.videos_queue[link] = quality
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

    def start_queue(self, queue_type: str) -> str:
        """
        Method to start queue with a desired queue type.
        :param queue_type: Type of the files we want to download (MP4, MP3, WAV, JPG or TAGS)
        :return: Success or failure message.
        """
        if queue_type == "mp4":
            if not self.videos_queue:
                return "Nothing to download, queue is empty."
            for link, quality in self.videos_queue.items():
                print(self.downloader.download_video(link, quality))
            self.videos_queue = {}
            return "All downloads have been finished."

        elif queue_type == "mp3":
            if not self.mp3_queue:
                return "Nothing to download, queue is empty."
            for link in self.mp3_queue:
                print(self.downloader.download_audio(link, "mp3"))
            self.mp3_queue = []
            return "All downloads have been finished."

        elif queue_type == "wav":
            if not self.wav_queue:
                return "Nothing to download, queue is empty."
            for link in self.wav_queue:
                print(self.downloader.download_audio(link, "wav"))
            self.wav_queue = []
            return "All downloads have been finished."

        elif queue_type == "jpg":
            if not self.thumbnail_queue:
                return "Nothing to download, queue is empty."
            for link in self.thumbnail_queue:
                print(self.thumbnail_downloader.download_thumbnail(link))
            self.thumbnail_queue = []
            return "All downloads have been finished."

        elif queue_type == "csv":
            if not self.tags_queue:
                return "Nothing to download, queue is empty."
            for link in self.tags_queue:
                print(self.tag_extractor.extract_tags(link, copy=False))
            self.tags_queue = []
            return "All downloads have been finished."
        else:
            return "Invalid queue type."

