import asyncio

from src.video_info import VideoInfo
from src.updater import initialize_binaries
from src.queue.download_queue import DownloadQueue

LINK = "https://youtu.be/dQw4w9WgXcQ?si=52ngrNGc_WNyEkUb"
LINK2 = "https://youtu.be/njX2bu-_Vw4?si=VgF6vfdYZFh9dhPe"
LINK3 = "https://youtu.be/xOMMV_qXcQ8?si=q5pqhGOqFbcr4acG"


async def main() -> None:
    """
    Main function of the program.
    """
    print("=" * 50)
    await initialize_binaries()
    print("=" * 50)
    print()

    video_info: VideoInfo = VideoInfo()
    queue: DownloadQueue = DownloadQueue()

    for information in await video_info.get_video_info(LINK):
        print(information)

    print(queue.add_video(LINK, 240))
    print(queue.add_video(LINK, 360))
    print(queue.add_video(LINK2, 240))
    print(queue.add_video(LINK3, 240))

    print(queue.add_mp3_audio(LINK))
    print(queue.add_mp3_audio(LINK2))
    print(queue.add_mp3_audio(LINK3))

    print(queue.add_wav_audio(LINK))
    print(queue.add_wav_audio(LINK2))
    print(queue.add_wav_audio(LINK3))

    print(queue.add_thumbnail(LINK))
    print(queue.add_thumbnail(LINK2))
    print(queue.add_thumbnail(LINK3))

    print(queue.add_tags(LINK))
    print(queue.add_tags(LINK2))
    print(queue.add_tags(LINK3))

    results = await asyncio.gather(
        queue.start_queue("mp4"),
        queue.start_queue("mp3"),
        queue.start_queue("wav"),
        queue.start_queue("jpg"),
        queue.start_queue("csv"),
    )

    for result in results:
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
