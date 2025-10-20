from downloader import Downloader
from thumbnail_downloader import ThumbnailDownloader
from video_info import VideoInfo
from tag_extractor import TagExtractor

LINK = "https://youtu.be/dQw4w9WgXcQ?si=52ngrNGc_WNyEkUb"


def main() -> None:
    """
    Main function of the program.
    """
    video_info: VideoInfo = VideoInfo()
    downloader: Downloader = Downloader(video_info)
    thumbnail_downloader: ThumbnailDownloader = ThumbnailDownloader(video_info)
    tag_extractor: TagExtractor = TagExtractor(video_info)

    for information in video_info.get_video_info(LINK):
        print(information)

    print(downloader.download_video(LINK, 1440))

    print(downloader.download_audio(LINK, "mp3"))
    print(thumbnail_downloader.download_thumbnail(LINK))
    print(tag_extractor.extract_tags(LINK))


if __name__ == "__main__":
    main()
