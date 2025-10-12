from video_info import VideoInfo


def main() -> None:
    """
    Main function of the program.
    """
    video_info = VideoInfo()
    for info in video_info.get_video_info("https://youtu.be/dQw4w9WgXcQ?si=SPIt6zX1gx9NouFZ"):
        print(info)


if __name__ == "__main__":
    main()
