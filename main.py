from video_info import VideoInfo


def main() -> None:
    """
    Main function of the program.
    """
    video_info = VideoInfo()
    print(video_info.get_video_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ&start_radio=1"))

if __name__ == "__main__":
    main()
