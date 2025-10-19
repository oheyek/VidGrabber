from downloader import Downloader
from video_info import VideoInfo

LINK = "https://youtu.be/dQw4w9WgXcQ?si=52ngrNGc_WNyEkUb"


def main() -> None:
    """
    Main function of the program.
    """
    video_info: VideoInfo = VideoInfo()
    downloader: Downloader = Downloader(video_info)
    for information in video_info.get_video_info(LINK):
        print(information)

    print(downloader.download_video(LINK, 1440))

    print(downloader.download_audio(LINK, "mp3"))


if __name__ == "__main__":
    main()
