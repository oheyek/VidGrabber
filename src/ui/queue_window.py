import asyncio
import threading

import customtkinter as ctk

from src.queue.download_queue import DownloadQueue


class QueueWindow(ctk.CTkToplevel):
    def __init__(self, parent, download_queue: DownloadQueue):
        super().__init__(parent)
        self.master = parent
        self.queue = download_queue

        self.title("Queue Manager")
        self.geometry("800x600")
        self.resizable(False, False)

        header = ctk.CTkLabel(
            self,
            text="📋 Download Queue Manager",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header.pack(pady=15)

        self.queue_display = ctk.CTkScrollableFrame(
            self, width=740, height=450
        )
        self.queue_display.pack(pady=10, padx=20, fill="both", expand=True)

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=10)

        refresh_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Refresh",
            command=self.refresh_queue_display,
            width=120
        )
        refresh_btn.pack(side="left", padx=5)

        start_all_btn = ctk.CTkButton(
            button_frame,
            text="▶️ Download All",
            command=self.start_all_downloads,
            width=150,
            fg_color="green",
            hover_color="darkgreen"
        )
        start_all_btn.pack(side="left", padx=5)

        clear_all_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Clear All",
            command=self.clear_all_queues,
            width=120,
            fg_color="red",
            hover_color="darkred"
        )
        clear_all_btn.pack(side="left", padx=5)

        self.refresh_queue_display()

    def refresh_queue_display(self):
        for widget in self.queue_display.winfo_children():
            widget.destroy()

        has_items = False

        if self.queue.videos_queue:
            has_items = True
            items = []
            for link, qualities in self.queue.videos_queue.items():
                for quality_tuple in qualities:
                    quality = quality_tuple[0]
                    items.append((link, quality))
            self._create_queue_section("🎬 Videos (MP4)", items, "mp4")

        if self.queue.mp3_queue:
            has_items = True
            self._create_queue_section("🎵 Audio (MP3)", self.queue.mp3_queue, "mp3")

        if self.queue.wav_queue:
            has_items = True
            self._create_queue_section("🎵 Audio (WAV)", self.queue.wav_queue, "wav")

        if self.queue.thumbnail_queue:
            has_items = True
            self._create_queue_section(
                "🖼️ Thumbnails (JPG)", self.queue.thumbnail_queue, "jpg"
            )

        if self.queue.tags_queue:
            has_items = True
            self._create_queue_section("🏷️ Tags (CSV)", self.queue.tags_queue, "csv")

        if not has_items:
            empty_label = ctk.CTkLabel(
                self.queue_display,
                text="Queue is empty",
                font=ctk.CTkFont(size=16),
                text_color="gray",
            )
            empty_label.pack(pady=50)

    def _create_queue_section(self, title: str, items, queue_type: str):
        section_frame = ctk.CTkFrame(self.queue_display)
        section_frame.pack(pady=10, padx=10, fill="x")

        header_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=5)

        title_label = ctk.CTkLabel(
            header_frame, text=title, font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(side="left")

        if queue_type == "mp4":
            for link, quality_list in self.queue.videos_queue.items():
                for quality_tuple in quality_list:
                    quality = quality_tuple[0]
                    video_title = quality_tuple[1]
                    self._create_queue_item(
                        section_frame,
                        link,
                        queue_type,
                        quality=quality,
                        display_text=video_title,
                        extra_info=f"{quality}p",
                    )
        else:
            for item in items:
                self._create_queue_item(
                    section_frame, item.link, queue_type, display_text=item.title
                )

    def _create_queue_item(
        self,
        parent,
        link: str,
        queue_type: str,
        quality: int = None,
        display_text: str = None,
        extra_info: str = None,
    ):
        item_frame = ctk.CTkFrame(parent)
        item_frame.pack(pady=3, padx=10, fill="x")

        text = display_text if display_text else link
        if len(text) > 60:
            text = text[:57] + "..."
        if extra_info:
            text = f"{text} [{extra_info}]"

        link_label = ctk.CTkLabel(item_frame, text=text, anchor="w")
        link_label.pack(side="left", padx=10, fill="x", expand=True)

        remove_btn = ctk.CTkButton(
            item_frame,
            text="✕",
            width=30,
            command=lambda: self._remove_item(link, queue_type, quality),
            fg_color="red",
            hover_color="darkred",
        )
        remove_btn.pack(side="right", padx=5)

    def _remove_item(self, link: str, queue_type: str, quality: int = None):
        if queue_type == "mp4":
            self.remove_video_item(link, quality)
        elif queue_type in ["mp3", "wav"]:
            self.remove_audio_item(link, queue_type)
        else:
            self.remove_other_item(link, queue_type)

    def remove_video_item(self, link: str, quality: int) -> None:
        if link in self.queue.videos_queue:
            self.queue.videos_queue[link] = [
                q for q in self.queue.videos_queue[link] if q[0] != quality
            ]
            if not self.queue.videos_queue[link]:
                del self.queue.videos_queue[link]
        self.refresh_queue_display()

    def remove_audio_item(self, link: str, queue_type: str) -> None:
        if queue_type == "mp3":
            self.queue.mp3_queue = [
                item for item in self.queue.mp3_queue if item.link != link
            ]
        elif queue_type == "wav":
            self.queue.wav_queue = [
                item for item in self.queue.wav_queue if item.link != link
            ]
        self.refresh_queue_display()

    def remove_other_item(self, link: str, queue_type: str) -> None:
        if queue_type == "jpg":
            self.queue.thumbnail_queue = [
                item for item in self.queue.thumbnail_queue if item.link != link
            ]
        elif queue_type == "csv":
            self.queue.tags_queue = [
                item for item in self.queue.tags_queue if item.link != link
            ]
        self.refresh_queue_display()

    def clear_all_queues(self) -> None:
        self.queue.videos_queue.clear()
        self.queue.mp3_queue.clear()
        self.queue.wav_queue.clear()
        self.queue.thumbnail_queue.clear()
        self.queue.tags_queue.clear()

        if hasattr(self.master, 'download_info'):
            self.master.after(0, lambda: self.master.download_info.configure(text=""))

        self.refresh_queue_display()

    def start_all_downloads(self) -> None:
        def async_download():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                tasks = []

                if self.queue.videos_queue:
                    tasks.append(loop.run_until_complete(self.queue.start_queue("mp4")))
                if self.queue.mp3_queue:
                    tasks.append(loop.run_until_complete(self.queue.start_queue("mp3")))
                if self.queue.wav_queue:
                    tasks.append(loop.run_until_complete(self.queue.start_queue("wav")))
                if self.queue.thumbnail_queue:
                    tasks.append(loop.run_until_complete(self.queue.start_queue("jpg")))
                if self.queue.tags_queue:
                    tasks.append(loop.run_until_complete(self.queue.start_queue("csv")))

                if tasks:
                    if hasattr(self.master, 'download_info'):
                        self.master.after(
                            0,
                            lambda: self.master._show_temporary_message(
                                "✅ All downloads finished", "", duration=2000
                            )
                        )
                else:
                    if hasattr(self.master, 'download_info'):
                        self.master.after(
                            0,
                            lambda: self.master._show_temporary_message(
                                "Queue is empty", "", duration=2000
                            )
                        )

                self.after(200, self.refresh_queue_display)

            finally:
                loop.close()

        threading.Thread(target=async_download, daemon=True).start()
