import asyncio
import os
import sys
import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog
from typing import Any

import customtkinter as ctk

from src.downloader import Downloader
from src.path_manager import PathManager
from src.queue.download_queue import DownloadQueue
from src.tag_extractor import TagExtractor
from src.thumbnail_downloader import ThumbnailDownloader
from src.ui.queue_window import QueueWindow
from src.video_info import VideoInfo


def resource_path(relative_path: Any) -> str:
    """
    Function to get absolute path to resource, used for PyInstaller.
    :param relative_path: Relative path of the resource.
    :return: Absolute path for PyInstaller purpose.
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


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
        self.queue_window = None
        try:
            if sys.platform == "win32":
                self.iconbitmap(resource_path(os.path.join("src", "ui", "icons", "icon.ico")))

            else:
                icon_path = resource_path("src/ui/icons/icon.png")
                if os.path.exists(icon_path):
                    icon = tk.PhotoImage(file=icon_path)
                    self.iconphoto(True, icon)

            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme(resource_path(os.path.join("src", "ui", "themes", "basalt.json")))
        except Exception as e:
            print(f"Could not load the resource: {e}")
        self.title("VidGrabber (v1.0)")
        self.geometry("1000x350")
        self.resizable(False, False)
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)
        self.path_manager = PathManager()
        self.download_queue = DownloadQueue()
        self.queue_window = None
        self.current_title = ""

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

        ascii_label: ctk.CTkLabel = ctk.CTkLabel(self.main_frame, text=ascii_art,
                                                 font=ctk.CTkFont(family="Courier", size=13, weight="bold"),
                                                 justify="left", )
        ascii_label.pack(pady=(10, 5))
        self.download_info = ctk.CTkLabel(self.main_frame, text="", font=ctk.CTkFont(size=14), )
        self.download_info.pack(pady=(10, 5))

        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=600, mode="indeterminate")
        self.progress_bar.pack(pady=5)
        self.progress_bar.pack_forget()

        entry_row: ctk.CTkFrame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        entry_row.configure(width=640, height=35)
        entry_row.pack(pady=(5, 10), padx=10, anchor="n")
        entry_row.pack_propagate(False)

        self.link_field = ctk.CTkEntry(entry_row, placeholder_text="🔗 Paste YouTube link...", width=500, height=25,
                                       justify="left", )
        self.link_field.pack(side="left", padx=(0, 10))

        self.video_info_button = ctk.CTkButton(entry_row, text="🔎 Grab video", width=120, height=25,
                                               command=self.handle_get_link_info, )
        self.video_info_button.pack(side="left")

        operation_row: ctk.CTkFrame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        operation_row.configure(width=900, height=35)
        operation_row.pack(pady=(5, 10), padx=10, anchor="n")
        operation_row.pack_propagate(False)

        self.download_thumbnail_button = ctk.CTkButton(operation_row, text="🖼️ Download thumbnail (JPG)", width=60,
                                                       height=25, command=self.handle_download_thumbnail, )
        self.download_thumbnail_button.pack(side="left")
        self.download_thumbnail_button.configure(state="disabled")

        self.download_mp3_button = ctk.CTkButton(operation_row, text="🎵 Download MP3", width=60, height=25,
                                                 command=self.handle_download_mp3, )
        self.download_mp3_button.pack(side="left", padx=(10, 0))
        self.download_mp3_button.configure(state="disabled")

        self.download_wav_button = ctk.CTkButton(operation_row, text="🎵 Download WAV", width=60, height=25,
                                                 command=self.handle_download_wav, )
        self.download_wav_button.pack(side="left", padx=(10, 0))
        self.download_wav_button.configure(state="disabled")

        self.download_mp4_button = ctk.CTkButton(operation_row, text="🎬 Download MP4", width=60, height=25,
                                                 command=self.show_quality_selection, )
        self.download_mp4_button.pack(side="left", padx=(10, 0))
        self.download_mp4_button.configure(state="disabled")

        self.download_tags_button = ctk.CTkButton(operation_row, text="🏷️ Tags (CSV + Clipboard)", width=60, height=25,
                                                  command=self.handle_extract_tags, )
        self.download_tags_button.pack(side="left", padx=(10, 0))
        self.download_tags_button.configure(state="disabled")

        settings_queue_row = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        settings_queue_row.pack(pady=(5, 10))

        self.settings_button = ctk.CTkButton(settings_queue_row, text="⚙️ Settings", width=120, height=30,
                                             command=self.open_settings_window, )
        self.settings_button.pack(side="left", padx=5)

        self.queue_button = ctk.CTkButton(settings_queue_row, text="📋 Queue Manager", width=120, height=30,
                                          command=self.open_queue_window, )
        self.queue_button.pack(side="left", padx=5)

    def _set_window_icon(self, window: ctk.CTkToplevel) -> None:
        """
        Helper method to set the icon for child windows (Toplevel).
        :param window: The window instance to set the icon for.
        """
        try:
            if sys.platform == "win32":
                icon_path = resource_path(os.path.join("src", "ui", "icons", "icon.ico"))
                window.after(300, lambda: window.iconbitmap(icon_path))
            else:
                icon_path = resource_path("src/ui/icons/icon.png")
                if os.path.exists(icon_path):
                    icon = tk.PhotoImage(file=icon_path)
                    window.iconphoto(True, icon)
        except Exception:
            pass

    def open_settings_window(self) -> None:
        """
        Open settings dialog window with theme and download path configuration.
        """
        settings = ctk.CTkToplevel(self)
        self._set_window_icon(settings)
        settings.title("Settings")
        settings.geometry("450x550")
        settings.resizable(False, False)
        settings.transient(self)
        if os.name == "nt":  # Windows
            settings.after(100, lambda: settings.grab_set())
        else:
            settings.update()
            settings.after(10, lambda: settings.grab_set())

        self.update_idletasks()
        settings.update_idletasks()

        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_width = self.winfo_width()
        main_height = self.winfo_height()

        dialog_width = settings.winfo_width()
        dialog_height = settings.winfo_height()

        x = main_x + (main_width - dialog_width) // 2
        y = main_y + (main_height - dialog_height) // 2
        settings.geometry(f"+{x}+{y}")

        title_label = ctk.CTkLabel(settings, text="⚙️ Settings", font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=(15, 10))

        # Tabs
        tabview = ctk.CTkTabview(settings, width=400, height=300, fg_color="transparent")
        tabview.pack(padx=20, pady=10)

        tabview.add("🎨 Appearance")
        tabview.add("📁 Downloads")
        tabview.add("ℹ️ Credits")

        # TAB 1: Appearance
        theme_label = ctk.CTkLabel(tabview.tab("🎨 Appearance"), text="Color Theme",
                                   font=ctk.CTkFont(size=14, weight="bold"))
        theme_label.pack(pady=(10, 5), anchor="w", padx=20)

        description_label = ctk.CTkLabel(tabview.tab("🎨 Appearance"), text="Choose your preferred color scheme:",
                                         font=ctk.CTkFont(size=11), text_color="gray")
        description_label.pack(pady=(0, 10), anchor="w", padx=20)

        current_theme = ctk.get_appearance_mode()
        theme_var = ctk.StringVar(value=current_theme)

        themes = [("🌙 Dark", "Dark", "Perfect for late-night coding"),
                  ("☀️ Light", "Light", "Easy on the eyes during daytime"),
                  ("💻 System", "System", "Follows your OS theme")]

        def change_theme(choice) -> None:
            """
            Helper function for changing window theme.
            :param choice: User's theme choice.
            """
            if settings.winfo_exists():
                settings.grab_release()

            ctk.set_appearance_mode(choice)

            def delayed_update() -> None:
                """
                Helper function to delay changing theme.
                """
                if not settings.winfo_exists():
                    return

                self.update_idletasks()
                settings.update_idletasks()

                self.download_info.configure(text=f"✅ Theme changed to {choice}")

            self.after(200, delayed_update)

        for label, value, desc in themes:
            theme_frame = ctk.CTkFrame(tabview.tab("🎨 Appearance"), fg_color="transparent")
            theme_frame.pack(pady=4, fill="x", anchor="w", padx=20)

            radio = ctk.CTkRadioButton(theme_frame, text=label, variable=theme_var, value=value,
                                       command=lambda v=value: change_theme(v),
                                       font=ctk.CTkFont(size=13, weight="bold"))
            radio.pack(anchor="w")

            desc_label = ctk.CTkLabel(theme_frame, text=f"   {desc}", font=ctk.CTkFont(size=10), text_color="gray")
            desc_label.pack(anchor="w", padx=(25, 0))

        # TAB 2: Downloads
        path_label = ctk.CTkLabel(tabview.tab("📁 Downloads"), text="Downloads Location",
                                  font=ctk.CTkFont(size=14, weight="bold"))
        path_label.pack(pady=(10, 5), anchor="w", padx=20)

        self._create_path_selector(tabview.tab("📁 Downloads"), "Thumbnails (JPG)", "jpg")
        self._create_path_selector(tabview.tab("📁 Downloads"), "Audio (MP3)", "mp3")
        self._create_path_selector(tabview.tab("📁 Downloads"), "Audio (WAV)", "wav")
        self._create_path_selector(tabview.tab("📁 Downloads"), "Video (MP4)", "mp4")
        self._create_path_selector(tabview.tab("📁 Downloads"), "Tags (CSV)", "tags")

        # TAB 3: Credits
        credits_frame = ctk.CTkFrame(tabview.tab("ℹ️ Credits"), fg_color="transparent")
        credits_frame.pack(pady=20, padx=20, fill="both", expand=True)

        app_label = ctk.CTkLabel(credits_frame, text="VidGrabber (1.0)", font=ctk.CTkFont(size=20, weight="bold"))
        app_label.pack(pady=(10, 5))

        version_label = ctk.CTkLabel(credits_frame, text="Desktop YouTube Downloader.", font=ctk.CTkFont(size=12),
                                     text_color="gray")
        version_label.pack(pady=(0, 20))

        github_label = ctk.CTkLabel(credits_frame, text="👨‍💻 Developer", font=ctk.CTkFont(size=14, weight="bold"))
        github_label.pack(pady=(10, 5))

        def open_github():
            """Open GitHub profile in browser."""

            webbrowser.open("https://github.com/oheyek")

        github_button = ctk.CTkButton(credits_frame, text="🔗 View on GitHub", command=open_github,
                                      font=ctk.CTkFont(size=13), width=200, height=35)
        github_button.pack(pady=5)

        separator = ctk.CTkLabel(credits_frame, text="───────────", text_color="gray")
        separator.pack(pady=15)

        support_label = ctk.CTkLabel(credits_frame, text="☕ Support Development",
                                     font=ctk.CTkFont(size=14, weight="bold"))
        support_label.pack(pady=(5, 10))

        def open_coffee():
            """Open Buy Me a Coffee page in browser."""
            import webbrowser
            webbrowser.open("https://buymeacoffee.com/ohey")

        coffee_button = ctk.CTkButton(credits_frame, text="☕ Buy Me a Coffee", command=open_coffee,
                                      font=ctk.CTkFont(size=13), fg_color="#FFDD00", text_color="black",
                                      hover_color="#FFE44D", width=200, height=35)
        coffee_button.pack(pady=5)

        footer_label = ctk.CTkLabel(credits_frame, text="Made with ❤️ by ohey.", font=ctk.CTkFont(size=10),
                                    text_color="gray")
        footer_label.pack(pady=(20, 0), side="bottom")

    def open_queue_window(self) -> None:
        """
        Open queue manager window to view and manage download queue.
        """
        if self.queue_window is None or not self.queue_window.winfo_exists():
            self.queue_window = QueueWindow(self, self.download_queue)
            self._set_window_icon(self.queue_window)
        else:
            self.queue_window.focus()

    def _show_temporary_message(self, message: str, original_text: str, duration: int = 2000) -> None:
        """
        Show temporary message and restore original text after duration.
        :param message: Temporary message to show.
        :param original_text: Original message text to restore.
        :param duration: Duration in milliseconds before restoring original text.
        """
        self.download_info.configure(text=message)
        if original_text:
            self.after(duration, lambda: self.download_info.configure(text=original_text))
        else:
            self.after(duration, lambda: self.download_info.configure(text=""))

    def _set_all_buttons_state(self, state: str) -> None:
        """
        Enable or disable all operation buttons.
        :param state: State of the button (disabled/normal).
        """
        self.video_info_button.configure(state=state)
        self.download_thumbnail_button.configure(state=state)
        self.download_mp3_button.configure(state=state)
        self.download_wav_button.configure(state=state)
        self.download_mp4_button.configure(state=state)
        self.download_tags_button.configure(state=state)

    def _run_async_operation(self, loading_msg: str, success_msg: str, error_msg: str, coroutine_func, *args, ) -> None:
        """
        Run an asynchronous operation in a separate daemon thread and update the UI.
        :param loading_msg: Message shown while the coroutine is running.
        :param success_msg: Message shown when the operation is considered successful.
        :param error_msg: Message or prefix shown when the operation fails.
        :param coroutine_func: Async function to be executed.
        :param args: Positional arguments forwarded to `coroutine_func`.
        """
        self._set_all_buttons_state("disabled")
        self.download_info.configure(text=loading_msg)
        self._is_downloading = True

        self.progress_bar.pack(pady=5)
        self.progress_bar.start()

        async def run_operation():
            """
            Execute the coroutine and handle the result with UI updates.
            """
            result = await coroutine_func(*args)

            self.progress_bar.stop()
            self.progress_bar.pack_forget()

            if isinstance(result, bool):
                if result:
                    self.download_info.configure(text=success_msg)
                else:
                    self.download_info.configure(text=error_msg)
            elif isinstance(result, str):
                if (
                        "completed" in result.lower() or "saved to file" in result.lower() or "copied to clipboard" in result.lower()):
                    self.download_info.configure(text=success_msg)
                else:
                    self.download_info.configure(text=f"{error_msg}: {result}")

            self._set_all_buttons_state("enabled")
            self._is_downloading = False

        def run():
            """
            Run the async operation in the current thread's event loop.
            """
            asyncio.run(run_operation())

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def handle_get_link_info(self) -> None:
        """
        Synchronous wrapper for the async get_link_info method.
        Run the async function in a separate thread to avoid event loop conflicts.
        """
        self._set_all_buttons_state("disabled")

        if self.queue_window and self.queue_window.winfo_exists():
            self.queue_window._set_download_buttons_state("disabled")

        self.download_info.configure(text="📥 Downloading video data...")
        thread: threading.Thread = threading.Thread(target=self._run_async_task, daemon=True)
        thread.start()

    def _run_async_task(self) -> None:
        """
        Helper method to run async task in a separate thread with progress bar indication.
        """
        self.progress_bar.pack(pady=5)
        self.progress_bar.start()

        asyncio.run(self.get_link_info())

        self.progress_bar.stop()
        self.progress_bar.pack_forget()

    async def get_link_info(self) -> None:
        """
        Async method to get video information from a YouTube link and display it in the UI.
        Fetches title and available video qualities from the provided YouTube URL.
        """
        link: str = self.link_field.get()
        self.current_link = link
        video_info: VideoInfo = VideoInfo()
        result = await video_info.get_video_info(link)

        if isinstance(result, list):
            title = result[0]
            self.current_title = title
            self.available_qualities = [q for q in result[4:] if q.startswith("mp4")]
            self.download_info.configure(text=title)
            self._set_all_buttons_state("enabled")

            if self.queue_window and self.queue_window.winfo_exists():
                self.queue_window._set_download_buttons_state("normal")
        else:
            self.current_title = ""
            self.download_info.configure(text=f"❌ {result}")
            self.video_info_button.configure(state="enabled")

            if self.queue_window and self.queue_window.winfo_exists():
                self.queue_window._set_download_buttons_state("normal")

    def handle_download_thumbnail(self) -> None:
        """
        Show dialog with Download/Add to Queue options for thumbnail download.
        Opens a modal dialog allowing user to immediately download or queue the thumbnail.
        """
        dialog = ctk.CTkToplevel(self)
        self._set_window_icon(dialog)
        dialog.title("Thumbnail Download")
        dialog.geometry("350x200")
        dialog.transient(self)
        dialog.after(100, lambda: dialog.grab_set())

        self.update_idletasks()
        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_width = self.winfo_width()
        main_height = self.winfo_height()
        x = main_x + (main_width - 350) // 2
        y = main_y + (main_height - 200) // 2
        dialog.geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(dialog, text="🖼️ Thumbnail (JPG)", font=ctk.CTkFont(size=16, weight="bold"))
        label.pack(pady=30)

        def download_now():
            """
            Start immediate thumbnail download without adding to queue.
            """
            dialog.destroy()

            async def download():
                link = self.link_field.get()
                video_info = VideoInfo()
                thumbnail_downloader = ThumbnailDownloader(video_info=video_info, path_manager=self.path_manager)
                return await thumbnail_downloader.download_thumbnail(link)

            self._run_async_operation("🖼️ Downloading thumbnail...", "✅ Thumbnail downloaded!", "❌ Failed", download, )

        def add_to_queue():
            """
            Add thumbnail download task to the download queue.
            """
            dialog.destroy()
            link = self.link_field.get()

            def async_add():
                """
                Execute queue addition in a separate async event loop.
                """
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    self.after(0, lambda: self._set_all_buttons_state("disabled"))
                    self.after(0, lambda: self.settings_button.configure(state="normal"))
                    self.after(0, lambda: self.queue_button.configure(state="normal"))

                    result = loop.run_until_complete(self.download_queue.add_thumbnail(link, self.current_title))

                    if "added to queue" in result.lower():
                        self.after(0, lambda: self._show_temporary_message(f"✅ {result}", "", duration=1500), )
                    else:
                        self.after(0, lambda: self._show_temporary_message(f"⚠️ {result}", "", duration=2000), )

                    if self.queue_window and self.queue_window.winfo_exists():
                        self.after(100, lambda: self.queue_window.refresh_queue_display())

                    self.after(0, lambda: self._set_all_buttons_state("enabled"))
                finally:
                    loop.close()

            threading.Thread(target=async_add, daemon=True).start()

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="✖️ Cancel", command=dialog.destroy, width=100).pack(side="left", padx=5)

        ctk.CTkButton(btn_frame, text="➕ Add to Queue", command=add_to_queue, width=120, fg_color="orange",
                      hover_color="darkorange", ).pack(side="left", padx=5)

        ctk.CTkButton(btn_frame, text="⬇️ Download", command=download_now, width=100).pack(side="left", padx=5)

    def handle_download_mp3(self) -> None:
        """
        Show dialog with Download/Add to Queue options for MP3 audio download.
        Opens a modal dialog allowing user to immediately download or queue the MP3 audio.
        """
        dialog = ctk.CTkToplevel(self)
        self._set_window_icon(dialog)
        dialog.title("MP3 Download")
        dialog.geometry("350x200")
        dialog.transient(self)
        dialog.after(100, lambda: dialog.grab_set())

        self.update_idletasks()
        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_width = self.winfo_width()
        main_height = self.winfo_height()
        x = main_x + (main_width - 350) // 2
        y = main_y + (main_height - 200) // 2
        dialog.geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(dialog, text="🎵 MP3 Audio", font=ctk.CTkFont(size=16, weight="bold"))
        label.pack(pady=30)

        def download_now():
            """
            Start immediate MP3 download without adding to queue.
            """
            dialog.destroy()

            async def download():
                link = self.link_field.get()
                video_info = VideoInfo()
                mp3_downloader = Downloader(video_info=video_info, path_manager=self.path_manager)
                return await mp3_downloader.download_audio(link, audio_format="mp3")

            self._run_async_operation("🎵 Downloading MP3...", "✅ MP3 downloaded!", "❌ Failed", download)

        def add_to_queue():
            """
            Add MP3 download task to the download queue.
            """
            dialog.destroy()
            link = self.link_field.get()

            def async_add():
                """
                Execute queue addition in a separate async event loop.
                """
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    self.after(0, lambda: self._set_all_buttons_state("disabled"))
                    self.after(0, lambda: self.settings_button.configure(state="normal"))
                    self.after(0, lambda: self.queue_button.configure(state="normal"))

                    result = loop.run_until_complete(self.download_queue.add_mp3_audio(link, self.current_title))

                    if "added to queue" in result.lower():
                        self.after(0, lambda: self._show_temporary_message(f"✅ {result}", "", duration=1500), )
                    else:
                        self.after(0, lambda: self._show_temporary_message(f"⚠️ {result}", "", duration=2000), )

                    if self.queue_window and self.queue_window.winfo_exists():
                        self.after(100, lambda: self.queue_window.refresh_queue_display())

                    self.after(0, lambda: self._set_all_buttons_state("enabled"))
                finally:
                    loop.close()

            threading.Thread(target=async_add, daemon=True).start()

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="✖️ Cancel", command=dialog.destroy, width=100).pack(side="left", padx=5)

        ctk.CTkButton(btn_frame, text="➕ Add to Queue", command=add_to_queue, width=120, fg_color="orange",
                      hover_color="darkorange", ).pack(side="left", padx=5)

        ctk.CTkButton(btn_frame, text="⬇️ Download", command=download_now, width=100).pack(side="left", padx=5)

    def handle_download_wav(self) -> None:
        """
        Show dialog with Download/Add to Queue options for WAV audio download.
        Opens a modal dialog allowing user to immediately download or queue the WAV audio.
        """
        dialog = ctk.CTkToplevel(self)
        self._set_window_icon(dialog)
        dialog.title("WAV Download")
        dialog.geometry("350x200")
        dialog.transient(self)
        dialog.after(100, lambda: dialog.grab_set())

        self.update_idletasks()
        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_width = self.winfo_width()
        main_height = self.winfo_height()
        x = main_x + (main_width - 350) // 2
        y = main_y + (main_height - 200) // 2
        dialog.geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(dialog, text="🎵 WAV Audio", font=ctk.CTkFont(size=16, weight="bold"))
        label.pack(pady=30)

        def download_now():
            """
            Start immediate WAV download without adding to queue.
            """
            dialog.destroy()

            async def download():
                link = self.link_field.get()
                video_info = VideoInfo()
                wav_downloader = Downloader(video_info=video_info, path_manager=self.path_manager)
                return await wav_downloader.download_audio(link, audio_format="wav")

            self._run_async_operation("🎵 Downloading WAV...", "✅ WAV downloaded!", "❌ Failed", download)

        def add_to_queue():
            """
            Add WAV download task to the download queue.
            """
            dialog.destroy()
            link = self.link_field.get()

            def async_add():
                """
                Execute queue addition in a separate async event loop.
                """
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    self.after(0, lambda: self._set_all_buttons_state("disabled"))
                    self.after(0, lambda: self.settings_button.configure(state="normal"))
                    self.after(0, lambda: self.queue_button.configure(state="normal"))

                    result = loop.run_until_complete(self.download_queue.add_wav_audio(link, self.current_title))

                    if "added to queue" in result.lower():
                        self.after(0, lambda: self._show_temporary_message(f"✅ {result}", "", duration=1500), )
                    else:
                        self.after(0, lambda: self._show_temporary_message(f"⚠️ {result}", "", duration=2000), )

                    if self.queue_window and self.queue_window.winfo_exists():
                        self.after(100, lambda: self.queue_window.refresh_queue_display())

                    self.after(0, lambda: self._set_all_buttons_state("enabled"))
                finally:
                    loop.close()

            threading.Thread(target=async_add, daemon=True).start()

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="✖️ Cancel", command=dialog.destroy, width=100).pack(side="left", padx=5)

        ctk.CTkButton(btn_frame, text="➕ Add to Queue", command=add_to_queue, width=120, fg_color="orange",
                      hover_color="darkorange", ).pack(side="left", padx=5)

        ctk.CTkButton(btn_frame, text="⬇️ Download", command=download_now, width=100).pack(side="left", padx=5)

    def handle_extract_tags(self) -> None:
        """
        Show dialog with Extract/Add to Queue options for tag extraction.
        Opens a modal dialog allowing user to immediately extract or queue the tag extraction.
        """
        dialog = ctk.CTkToplevel(self)
        self._set_window_icon(dialog)
        dialog.title("Tags Extraction")
        dialog.geometry("350x200")
        dialog.transient(self)
        dialog.after(100, lambda: dialog.grab_set())

        self.update_idletasks()
        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_width = self.winfo_width()
        main_height = self.winfo_height()
        x = main_x + (main_width - 350) // 2
        y = main_y + (main_height - 200) // 2
        dialog.geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(dialog, text="🏷️ Tags (CSV)", font=ctk.CTkFont(size=16, weight="bold"))
        label.pack(pady=30)

        def extract_now():
            """
            Start immediate tag extraction without adding to queue.
            """
            dialog.destroy()

            async def extract():
                link = self.link_field.get()
                video_info = VideoInfo()
                tag_extract = TagExtractor(video_info=video_info, path_manager=self.path_manager)
                return await tag_extract.extract_tags(link)

            self._run_async_operation("🏷️ Extracting tags...", "✅ Tags extracted!", "❌ Failed", extract)

        def add_to_queue():
            """
            Add tag extraction task to the download queue.
            """
            dialog.destroy()
            link = self.link_field.get()

            def async_add():
                """
                Execute queue addition in a separate async event loop.
                """
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    self.after(0, lambda: self._set_all_buttons_state("disabled"))
                    self.after(0, lambda: self.settings_button.configure(state="normal"))
                    self.after(0, lambda: self.queue_button.configure(state="normal"))

                    result = loop.run_until_complete(self.download_queue.add_tags(link, self.current_title))

                    if "added to queue" in result.lower():
                        self.after(0, lambda: self._show_temporary_message(f"✅ {result}", "", duration=1500), )
                    else:
                        self.after(0, lambda: self._show_temporary_message(f"⚠️ {result}", "", duration=2000), )

                    if self.queue_window and self.queue_window.winfo_exists():
                        self.after(100, lambda: self.queue_window.refresh_queue_display())

                    self.after(0, lambda: self._set_all_buttons_state("enabled"))
                finally:
                    loop.close()

            threading.Thread(target=async_add, daemon=True).start()

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="✖️ Cancel", command=dialog.destroy, width=100).pack(side="left", padx=5)

        ctk.CTkButton(btn_frame, text="➕ Add to Queue", command=add_to_queue, width=120, fg_color="orange",
                      hover_color="darkorange", ).pack(side="left", padx=5)

        ctk.CTkButton(btn_frame, text="🔍 Extract", command=extract_now, width=100).pack(side="left", padx=5)

    def show_quality_selection(self) -> None:
        """
        Show video quality selection dialog for MP4 download.
        Displays available video qualities and allows user to select preferred quality.
        """
        if not self.available_qualities:
            self.download_info.configure(text="❌ No quality options available")
            return

        base_height = 200
        quality_height = len(self.available_qualities) * 40
        total_height = min(base_height + quality_height, 600)

        dialog = ctk.CTkToplevel(self)
        self._set_window_icon(dialog)
        dialog.title("Select Video Quality")
        dialog.geometry(f"400x{total_height}")
        dialog.transient(self)
        dialog.after(100, lambda: dialog.grab_set())
        dialog.update_idletasks()

        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_width = self.winfo_width()
        main_height = self.winfo_height()

        dialog_width = 400
        dialog_height = total_height

        x = main_x + (main_width - dialog_width) // 2
        y = main_y + (main_height - dialog_height) // 2

        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        label = ctk.CTkLabel(dialog, text="Select video quality:", font=ctk.CTkFont(size=14, weight="bold"), )
        label.pack(pady=20)

        quality_frame = ctk.CTkScrollableFrame(dialog, width=350, height=min(quality_height, 300))
        quality_frame.pack(pady=10, padx=20, fill="both", expand=True)

        selected_quality = ctk.StringVar(value=self.available_qualities[0])

        for quality in self.available_qualities:
            radio = ctk.CTkRadioButton(quality_frame, text=quality, variable=selected_quality, value=quality,
                                       font=ctk.CTkFont(size=12), )
            radio.pack(pady=5, anchor="w", padx=10)

        def on_download():
            """
            Handle immediate video download with selected quality.
            """
            video_quality = selected_quality.get()
            dialog.destroy()
            self.handle_download_mp4(video_quality)

        def on_add_to_queue():
            """
            Add video download task with selected quality to the download queue.
            """
            video_quality = selected_quality.get()
            quality_height = int(video_quality.split()[1].rstrip("p"))
            dialog.destroy()
            link = self.current_link

            def async_add():
                """
                Execute queue addition in a separate async event loop.
                """
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    self.after(0, lambda: self._set_all_buttons_state("disabled"))
                    self.after(0, lambda: self.settings_button.configure(state="normal"))
                    self.after(0, lambda: self.queue_button.configure(state="normal"))

                    result = loop.run_until_complete(
                        self.download_queue.add_video(link, quality_height, self.current_title))

                    if "added to queue" in result.lower():
                        self.after(0, lambda: self._show_temporary_message(f"✅ {result}", "", duration=1500), )
                    else:
                        self.after(0, lambda: self._show_temporary_message(f"⚠️ {result}", "", duration=2000), )

                    if self.queue_window and self.queue_window.winfo_exists():
                        self.after(100, lambda: self.queue_window.refresh_queue_display())

                    self.after(0, lambda: self._set_all_buttons_state("enabled"))
                finally:
                    loop.close()

            threading.Thread(target=async_add, daemon=True).start()

        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20)

        cancel_btn = ctk.CTkButton(button_frame, text="✖️ Cancel", command=dialog.destroy, width=100)
        cancel_btn.pack(side="left", padx=5)

        queue_btn = ctk.CTkButton(button_frame, text="➕ Add to Queue", command=on_add_to_queue, width=120,
                                  fg_color="orange", hover_color="darkorange", )
        queue_btn.pack(side="left", padx=5)

        download_btn = ctk.CTkButton(button_frame, text="⬇️ Download", command=on_download, width=100)
        download_btn.pack(side="left", padx=5)

    def handle_download_mp4(self, quality: str) -> None:
        """
        Synchronous wrapper for the async download_mp4 method.
        :param quality: Video quality string containing resolution (e.g., "mp4 1080p").
        """

        async def download():
            """
            Execute the MP4 video download with specified quality.
            """
            quality_height = int(quality.split()[1].rstrip("p"))
            video_info = VideoInfo()
            mp4_downloader = Downloader(video_info=video_info, path_manager=self.path_manager)
            return await mp4_downloader.download_video(self.current_link, quality=quality_height)

        self._run_async_operation(f"🎬 Downloading MP4 ({quality})...", f"✅ MP4 ({quality}) downloaded successfully!",
                                  "❌ Failed to download MP4", download)

    @staticmethod
    def select_folder(entry: ctk.CTkEntry) -> None:
        """
        Open folder selection dialog and update entry widget with selected path.
        :param entry: Entry widget to be updated with selected folder path.
        """
        folder = filedialog.askdirectory(title="Select Download Folder",
                                         initialdir=entry.get() or os.path.expanduser("~/Downloads"))
        if folder:
            entry.delete(0, "end")
            entry.insert(0, folder)

    def _create_path_selector(self, parent: ctk.CTkFrame, label_text: str, extension: str) -> ctk.CTkEntry:
        """
        Create a standardized path selector with label, entry and browse button.
        :param parent: Parent frame to add the selector to.
        :param label_text: Label text to display above the selector.
        :param extension: File extension key (jpg, mp3, wav, mp4, tags).
        :return: The entry widget for potential later access.
        """
        label = ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(size=12, weight="bold"), text_color="gray70", )
        label.pack(pady=(5, 2), anchor="w", padx=20)

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=2)

        entry = ctk.CTkEntry(row, width=260, height=28, state="readonly")

        if extension in self.path_manager.paths:
            saved_path = str(self.path_manager.paths[extension])
        else:
            saved_path = str(Path.home() / "Downloads" / extension)

        entry.configure(state="normal")
        entry.insert(0, saved_path)
        entry.configure(state="readonly")
        entry.pack(side="left", padx=(0, 5))

        def on_browse():
            """
            Handle browse button click to open folder selection dialog.
            Updates path manager and saves settings when folder is selected.
            """
            if hasattr(self, "_is_downloading") and self._is_downloading:
                return

            if (hasattr(self, "queue_window") and self.queue_window and self.queue_window.winfo_exists() and hasattr(
                    self.queue_window, "_is_downloading") and self.queue_window._is_downloading):
                return

            folder = filedialog.askdirectory(title="Select Download Folder",
                                             initialdir=entry.get() or os.path.expanduser("~/Downloads"), )
            if folder:
                entry.configure(state="normal")
                entry.delete(0, "end")
                entry.insert(0, folder)
                entry.configure(state="readonly")
                self.path_manager.paths[extension] = Path(folder)
                self.path_manager.save_settings()
                self.download_info.configure(text=f"✅ Path for {extension} saved!")

        browse_btn = ctk.CTkButton(row, text="📂 Browse", width=70, height=28, command=on_browse, )
        browse_btn.pack(side="left")

        return entry
