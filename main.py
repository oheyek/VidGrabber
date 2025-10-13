from video_info import VideoInfo


def main() -> None:
    """
    Main function of the program.
    """
    video_info = VideoInfo()
    for information in video_info.get_video_info("https://youtu.be/dQw4w9WgXcQ?si=52ngrNGc_WNyEkUb"):
        print(information)


if __name__ == "__main__":
    main()
