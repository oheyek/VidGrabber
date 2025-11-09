import asyncio
import threading

import customtkinter as ctk

from src.downloader import Downloader
from src.tag_extractor import TagExtractor
from src.thumbnail_downloader import ThumbnailDownloader
from src.video_info import VideoInfo


class AppUI(ctk.CTk):
    video_info_button: ctk.CTkButton
    link_field: ctk.CTkEntry
    download_info: ctk.CTkLabel
    main_frame: ctk.CTkFrame
    available_qualities: list[str] = []
    current_link: str = ""

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

        operation_row: ctk.CTkFrame = ctk.CTkFrame(
            self.main_frame, fg_color="transparent"
        )
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
            command=self.show_quality_selection,
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

    def _set_all_buttons_state(self, state: str) -> None:
        """
        Enable or disable all operation buttons.
        :param: State of the button (disabled/enabled).
        """
        self.video_info_button.configure(state=state)
        self.download_thumbnail_button.configure(state=state)
        self.download_mp3_button.configure(state=state)
        self.download_wav_button.configure(state=state)
        self.download_mp4_button.configure(state=state)
        self.download_tags_button.configure(state=state)

    def _run_async_operation(
        self,
        button: ctk.CTkButton,
        loading_msg: str,
        success_msg: str,
        error_msg: str,
        coroutine_func,
        *args,
    ) -> None:
        """
        Universal method to run async operations with UI updates
        """
        self._set_all_buttons_state("disabled")
        self.download_info.configure(text=loading_msg)

        async def run_operation():
            result = await coroutine_func(*args)

            if isinstance(result, bool):
                if result:
                    self.download_info.configure(text=success_msg)
                else:
                    self.download_info.configure(text=error_msg)
            elif isinstance(result, str):
                if (
                    "completed" in result.lower()
                    or "saved to file" in result.lower()
                    or "copied to clipboard" in result.lower()
                ):
                    self.download_info.configure(text=success_msg)
                else:
                    self.download_info.configure(text=f"{error_msg}: {result}")

            self._set_all_buttons_state("enabled")

        def run():
            asyncio.run(run_operation())

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def handle_get_link_info(self) -> None:
        """
        Synchronous wrapper for the async get_link_info method
        Run the async function in a separate thread to avoid event loop conflicts
        """
        self._set_all_buttons_state("disabled")
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
        self.current_link = link
        video_info: VideoInfo = VideoInfo()
        result = await video_info.get_video_info(link)

        if isinstance(result, list):
            title = result[0]
            self.available_qualities = [q for q in result[4:] if q.startswith("mp4")]
        else:
            title = result
            self.available_qualities = []

        self.download_info.configure(text=title)
        self._set_all_buttons_state("enabled")

    def handle_download_thumbnail(self) -> None:
        """
        Synchronous wrapper for the async download_thumbnail method
        """
        async def download():
            link = self.link_field.get()
            video_info = VideoInfo()
            thumbnail_downloader = ThumbnailDownloader(video_info=video_info)
            return await thumbnail_downloader.download_thumbnail(link)

        self._run_async_operation(
            self.download_thumbnail_button,
            "Downloading thumbnail...",
            "Thumbnail downloaded successfully!",
            "Failed to download thumbnail",
            download
        )

    def handle_download_mp3(self) -> None:
        """
        Synchronous wrapper for the async download_mp3 method
        """
        async def download():
            link = self.link_field.get()
            video_info = VideoInfo()
            mp3_downloader = Downloader(video_info=video_info)
            return await mp3_downloader.download_audio(link, audio_format="mp3")

        self._run_async_operation(
            self.download_mp3_button,
            "Downloading MP3 audio...",
            "MP3 downloaded successfully!",
            "Failed to download MP3",
            download
        )

    def handle_download_wav(self) -> None:
        """
        Synchronous wrapper for the async download_wav method
        """
        async def download():
            link = self.link_field.get()
            video_info = VideoInfo()
            wav_downloader = Downloader(video_info=video_info)
            return await wav_downloader.download_audio(link, audio_format="wav")

        self._run_async_operation(
            self.download_wav_button,
            "Downloading WAV audio...",
            "WAV downloaded successfully!",
            "Failed to download WAV",
            download
        )

    def handle_extract_tags(self) -> None:
        """
        Synchronous wrapper for the async extract_tags method
        """
        async def extract():
            link = self.link_field.get()
            video_info = VideoInfo()
            tag_extract = TagExtractor(video_info=video_info)
            return await tag_extract.extract_tags(link)

        self._run_async_operation(
            self.download_tags_button,
            "Extracting video tags...",
            "Tags extracted to file and copied to clipboard!",
            "Failed to extract tags",
            extract
        )

    def show_quality_selection(self) -> None:
        """
        Show quality selection dialog
        """
        if not self.available_qualities:
            self.download_info.configure(text="No quality options available")
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Select Video Quality")
        dialog.geometry("400x400")
        dialog.transient(self)
        dialog.grab_set()

        label = ctk.CTkLabel(
            dialog,
            text="Select video quality:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        label.pack(pady=20)

        selected_quality = ctk.StringVar(value=self.available_qualities[0])

        for quality in self.available_qualities:
            radio = ctk.CTkRadioButton(
                dialog,
                text=quality,
                variable=selected_quality,
                value=quality,
                font=ctk.CTkFont(size=12),
            )
            radio.pack(pady=5)

        def on_download():
            quality = selected_quality.get()
            dialog.destroy()
            self.handle_download_mp4(quality)

        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20)

        cancel_btn = ctk.CTkButton(
            button_frame, text="Cancel", command=dialog.destroy, width=100
        )
        cancel_btn.pack(side="left", padx=5)

        download_btn = ctk.CTkButton(
            button_frame, text="Download", command=on_download, width=100
        )
        download_btn.pack(side="left", padx=5)

    def handle_download_mp4(self, quality: str) -> None:
        """
        Synchronous wrapper for the async download_mp4 method
        """
        async def download():
            quality_height = int(quality.split()[1].rstrip("p"))
            video_info = VideoInfo()
            mp4_downloader = Downloader(video_info=video_info)
            return await mp4_downloader.download_video(self.current_link, quality=quality_height)

        self._run_async_operation(
            self.download_mp4_button,
            f"Downloading MP4 ({quality})...",
            f"MP4 ({quality}) downloaded successfully!",
            "Failed to download MP4",
            download
        )