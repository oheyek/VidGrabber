import asyncio
import threading

import customtkinter as ctk

from src.tag_extractor import TagExtractor
from src.video_info import VideoInfo
from src.thumbnail_downloader import ThumbnailDownloader
from src.downloader import Downloader


class AppUI(ctk.CTk):
    video_info_button: ctk.CTkButton
    link_field: ctk.CTkEntry
    download_info: ctk.CTkLabel
    main_frame: ctk.CTkFrame

    def __init__(self) -> None:
        """
        Class of the app interface.
        """
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title("VidGrabber (v0.1)")
        self.geometry("1000x280")
        self.resizable(True, True)
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)

        # ASCII Art Banner
        ascii_art: str = r"""
        /$$    /$$ /$$       /$$  /$$$$$$                     /$$       /$$
       | $$   | $$|__/      | $$ /$$__  $$                   | $$      | $$
       | $$   | $$ /$$  /$$$$$$$| $$  \__/  /$$$$$$  /$$$$$$ | $$$$$$$ | $$$$$$$   /$$$$$$   /$$$$$$
       |  $$ / $$/| $$ /$$__  $$| $$ /$$$$ /$$__  $$|____  $$| $$__  $$| $$__  $$ /$$__  $$ /$$__  $$
        \  $$ $$/ | $$| $$  | $$| $$|_  $$| $$  \__/ /$$$$$$$| $$  \ $$| $$  \ $$| $$$$$$$$| $$  \__/
         \  $$$/  | $$| $$  | $$| $$  \ $$| $$      /$$__  $$| $$  | $$| $$  | $$| $$_____/| $$
          \  $/   | $$|  $$$$$$$|  $$$$$$/| $$     |  $$$$$$$| $$$$$$$/| $$$$$$$/|  $$$$$$$| $$
           \_/    |__/ \_______/ \______/ |__/      \_______/|_______/ |_______/  \_______/|__/"""

        ascii_label: ctk.CTkLabel = ctk.CTkLabel(
            self.main_frame,
            text=ascii_art,
            font=ctk.CTkFont(family="Courier", size=12, weight="bold"),
            justify="left",
        )
        ascii_label.pack(pady=(10, 5))
        self.download_info = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(size=14),
        )
        self.download_info.pack(pady=(10, 5))

        entry_row: ctk.CTkFrame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        entry_row.configure(width=640, height=35)
        entry_row.pack(pady=(5, 10), padx=10, anchor="n")
        entry_row.pack_propagate(False)

        self.link_field = ctk.CTkEntry(
            entry_row,
            placeholder_text="Paste YouTube video link...",
            width=500,
            height=25,
            justify="left",
        )
        self.link_field.pack(side="left", padx=(0, 10))

        self.video_info_button = ctk.CTkButton(
            entry_row,
            text="Grab the video",
            width=120,
            height=25,
            command=self.handle_get_link_info,
        )
        self.video_info_button.pack(side="left")

        operation_row: ctk.CTkFrame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        operation_row.configure(width=900, height=35)
        operation_row.pack(pady=(5, 10), padx=10, anchor="n")
        operation_row.pack_propagate(False)

        self.download_thumbnail_button = ctk.CTkButton(
            operation_row,
            text="Download thumbnail (JPG)",
            width=60,
            height=25,
            command=self.handle_download_thumbnail,
        )
        self.download_thumbnail_button.pack(side="left")
        self.download_thumbnail_button.configure(state="disabled")

        self.download_mp3_button = ctk.CTkButton(
            operation_row,
            text="Download audio (MP3)",
            width=60,
            height=25,
            command=self.handle_download_mp3,
        )
        self.download_mp3_button.pack(side="left", padx=(10, 0))
        self.download_mp3_button.configure(state="disabled")

        self.download_wav_button = ctk.CTkButton(
            operation_row,
            text="Download audio (WAV)",
            width=60,
            height=25,
            command=self.handle_download_wav,
        )
        self.download_wav_button.pack(side="left", padx=(10, 0))
        self.download_wav_button.configure(state="disabled")

        self.download_mp4_button = ctk.CTkButton(
            operation_row,
            text="Download video (MP4)",
            width=60,
            height=25,
        )
        self.download_mp4_button.pack(side="left", padx=(10, 0))
        self.download_mp4_button.configure(state="disabled")

        self.download_tags_button = ctk.CTkButton(
            operation_row,
            text="Download tags (CSV + Clipboard)",
            width=60,
            height=25,
            command=self.handle_extract_tags,
        )
        self.download_tags_button.pack(side="left", padx=(10, 0))
        self.download_tags_button.configure(state="disabled")

    def handle_get_link_info(self) -> None:
        """
        Synchronous wrapper for the async get_link_info method
        Run the async function in a separate thread to avoid event loop conflicts
        """
        self.video_info_button.configure(state="disabled")
        self.download_info.configure(text="Downloading video data...")
        thread: threading.Thread = threading.Thread(
            target=self._run_async_task, daemon=True
        )
        thread.start()

    def _run_async_task(self) -> None:
        """
        Helper method to run async task in a separate thread
        """
        asyncio.run(self.get_link_info())

    async def get_link_info(self) -> None:
        """
        Async method to get a title from a YouTube video and display it to UI.
        """
        link: str = self.link_field.get()
        video_info: VideoInfo = VideoInfo()
        title: str | list[str] = await video_info.get_video_info(link)
        if isinstance(title, list):
            title = title[0]
        self.download_info.configure(text=title)
        self.video_info_button.configure(state="enabled")
        self.download_thumbnail_button.configure(state="enabled")
        self.download_mp3_button.configure(state="enabled")
        self.download_wav_button.configure(state="enabled")
        self.download_mp4_button.configure(state="enabled")
        self.download_tags_button.configure(state="enabled")

    def handle_download_thumbnail(self) -> None:
        """
        Synchronous wrapper for the async download_thumbnail method
        """
        self.download_thumbnail_button.configure(state="disabled")
        self.download_info.configure(text="Downloading thumbnail...")
        thread: threading.Thread = threading.Thread(
            target=self._run_thumbnail_download, daemon=True
        )
        thread.start()

    def _run_thumbnail_download(self) -> None:
        """
        Helper method to run thumbnail download in a separate thread
        """
        asyncio.run(self.download_thumbnail())

    async def download_thumbnail(self) -> None:
        """
        Async method to download thumbnail from YouTube video
        """
        link: str = self.link_field.get()
        video_info: VideoInfo = VideoInfo()
        thumbnail_downloader: ThumbnailDownloader = ThumbnailDownloader(
            video_info=video_info
        )
        success: bool = await thumbnail_downloader.download_thumbnail(link)

        if success:
            self.download_info.configure(text="Thumbnail downloaded successfully!")
        else:
            self.download_info.configure(text="Failed to download thumbnail")

        self.download_thumbnail_button.configure(state="enabled")

    def handle_download_mp3(self) -> None:
        """
        Synchronous wrapper for the async download_mp3 method
        """
        self.download_mp3_button.configure(state="disabled")
        self.download_info.configure(text="Downloading MP3 audio...")
        thread: threading.Thread = threading.Thread(
            target=self._run_mp3_download, daemon=True
        )
        thread.start()

    def _run_mp3_download(self) -> None:
        """
        Helper method to run mp3 download in a separate thread
        """
        asyncio.run(self.download_mp3())

    async def download_mp3(self) -> None:
        """
        Async method to download mp3 from YouTube video
        """
        link: str = self.link_field.get()
        video_info: VideoInfo = VideoInfo()
        mp3_downloader: Downloader = Downloader(
            video_info=video_info
        )
        success: bool = await mp3_downloader.download_audio(link, audio_format="mp3")

        if success:
            self.download_info.configure(text="MP3 downloaded successfully!")
        else:
            self.download_info.configure(text="Failed to download MP3")

        self.download_mp3_button.configure(state="enabled")

    def handle_download_wav(self) -> None:
        """
        Synchronous wrapper for the async download_wav method
        """
        self.download_wav_button.configure(state="disabled")
        self.download_info.configure(text="Downloading WAV audio...")
        thread: threading.Thread = threading.Thread(
            target=self._run_wav_download, daemon=True
        )
        thread.start()

    def _run_wav_download(self) -> None:
        """
        Helper method to run wav download in a separate thread
        """
        asyncio.run(self.download_wav())

    async def download_wav(self) -> None:
        """
        Async method to download wav from YouTube video
        """
        link: str = self.link_field.get()
        video_info: VideoInfo = VideoInfo()
        wav_downloader: Downloader = Downloader(
            video_info=video_info
        )
        success: bool = await wav_downloader.download_audio(link, audio_format="wav")

        if success:
            self.download_info.configure(text="WAV downloaded successfully!")
        else:
            self.download_info.configure(text="Failed to download WAV")

        self.download_wav_button.configure(state="enabled")

    def handle_extract_tags(self) -> None:
        """
        Synchronous wrapper for the async extract_tags method
        """
        self.download_tags_button.configure(state="disabled")
        self.download_info.configure(text="Extracting video tags...")
        thread: threading.Thread = threading.Thread(
            target=self._run_tags_extract, daemon=True
        )
        thread.start()

    def _run_tags_extract(self) -> None:
        """
        Helper method to run tags extract in a separate thread
        """
        asyncio.run(self.extract_tags())

    async def extract_tags(self) -> None:
        """
        Async method to extract tags from YouTube video
        """
        link: str = self.link_field.get()
        video_info: VideoInfo = VideoInfo()
        tag_extract: TagExtractor = TagExtractor(
            video_info=video_info
        )
        success: bool = await tag_extract.extract_tags(link)

        if success:
            self.download_info.configure(text="Tags extracted to file and copied to clipboard!")
        else:
            self.download_info.configure(text="Failed to extract tags")

        self.download_tags_button.configure(state="enabled")



