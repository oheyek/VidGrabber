from downloader import Downloader
from video_info import VideoInfo


def main() -> None:
    """
    Main function of the program.
    """
    video_info: VideoInfo = VideoInfo()
    downloader: Downloader = Downloader(video_info)
    for information in video_info.get_video_info(
        "https://youtu.be/dQw4w9WgXcQ?si=52ngrNGc_WNyEkUb"
    ):
        print(information)

    print(
        downloader.download_video(
            "https://youtu.be/dQw4w9WgXcQ?si=52ngrNGc_WNyEkUb", 1440
        )
    )


if __name__ == "__main__":
    main()
