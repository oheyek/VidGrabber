import asyncio
import threading

import customtkinter as ctk

from src.queue.download_queue import DownloadQueue


class QueueWindow(ctk.CTkToplevel):
    def __init__(self, parent, download_queue: DownloadQueue):
        super().__init__(parent)
        self.download_queue = download_queue
        self.title("📋 Download Queue Manager")
        self.geometry("900x650")
        self.resizable(True, True)

        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        header = ctk.CTkLabel(
            main_container,
            text="Download Queue",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header.pack(pady=(10, 15))

        self.queue_display = ctk.CTkScrollableFrame(
            main_container,
            width=850,
            height=450,
            fg_color="transparent"
        )
        self.queue_display.pack(pady=10, padx=10, fill="both", expand=True)

        self.controls_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        self.controls_frame.pack(pady=10, fill="x", padx=20)

        self.start_mp4_btn = ctk.CTkButton(
            self.controls_frame,
            text="▶️ Start MP4 Queue",
            width=140,
            command=lambda: self.start_queue("mp4")
        )
        self.start_mp4_btn.pack(side="left", padx=5)

        self.start_mp3_btn = ctk.CTkButton(
            self.controls_frame,
            text="▶️ Start MP3 Queue",
            width=140,
            command=lambda: self.start_queue("mp3")
        )
        self.start_mp3_btn.pack(side="left", padx=5)

        self.start_wav_btn = ctk.CTkButton(
            self.controls_frame,
            text="▶️ Start WAV Queue",
            width=140,
            command=lambda: self.start_queue("wav")
        )
        self.start_wav_btn.pack(side="left", padx=5)

        self.start_jpg_btn = ctk.CTkButton(
            self.controls_frame,
            text="▶️ Start JPG Queue",
            width=140,
            command=lambda: self.start_queue("jpg")
        )
        self.start_jpg_btn.pack(side="left", padx=5)

        self.start_csv_btn = ctk.CTkButton(
            self.controls_frame,
            text="▶️ Start Tags Queue",
            width=140,
            command=lambda: self.start_queue("csv")
        )
        self.start_csv_btn.pack(side="left", padx=5)

        self.refresh_btn = ctk.CTkButton(
            self.controls_frame,
            text="🔄 Refresh",
            width=100,
            command=self.refresh_queue_display
        )
        self.refresh_btn.pack(side="right", padx=5)

        self.clear_btn = ctk.CTkButton(
            self.controls_frame,
            text="🗑️ Clear All",
            width=120,
            fg_color="red",
            hover_color="darkred",
            command=self.clear_all_queues
        )
        self.clear_btn.pack(side="right", padx=5)

        self.status_label = ctk.CTkLabel(
            main_container,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=5)

        self.refresh_queue_display()

    def refresh_queue_display(self):
        for widget in self.queue_display.winfo_children():
            widget.destroy()

        # MP4 Videos
        mp4_header = ctk.CTkLabel(
            self.queue_display,
            text="🎬 MP4 Videos",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1f6aa5"
        )
        mp4_header.pack(pady=(5, 5), anchor="w")

        if self.download_queue.videos_queue:
            for link, qualities in self.download_queue.videos_queue.items():
                for quality in qualities:
                    self._create_queue_item(
                        f"Video ({quality}p): {link[:60]}...",
                        lambda l=link, q=quality: self._remove_video(l, q)
                    )
        else:
            empty_label = ctk.CTkLabel(
                self.queue_display,
                text="  📭 No MP4 videos in queue",
                text_color="gray",
                font=ctk.CTkFont(size=11, slant="italic")
            )
            empty_label.pack(pady=5, anchor="w")

        ctk.CTkFrame(self.queue_display, height=2, fg_color="gray30").pack(fill="x", pady=10)

        # MP3 Audio
        mp3_header = ctk.CTkLabel(
            self.queue_display,
            text="🎵 MP3 Audio",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1f6aa5"
        )
        mp3_header.pack(pady=(5, 5), anchor="w")

        if self.download_queue.mp3_queue:
            for link in self.download_queue.mp3_queue:
                self._create_queue_item(
                    f"MP3: {link[:60]}...",
                    lambda l=link: self._remove_mp3(l)
                )
        else:
            empty_label = ctk.CTkLabel(
                self.queue_display,
                text="  📭 No MP3 audio in queue",
                text_color="gray",
                font=ctk.CTkFont(size=11, slant="italic")
            )
            empty_label.pack(pady=5, anchor="w")

        ctk.CTkFrame(self.queue_display, height=2, fg_color="gray30").pack(fill="x", pady=10)

        # WAV Audio
        wav_header = ctk.CTkLabel(
            self.queue_display,
            text="🎵 WAV Audio",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1f6aa5"
        )
        wav_header.pack(pady=(5, 5), anchor="w")

        if self.download_queue.wav_queue:
            for link in self.download_queue.wav_queue:
                self._create_queue_item(
                    f"WAV: {link[:60]}...",
                    lambda l=link: self._remove_wav(l)
                )
        else:
            empty_label = ctk.CTkLabel(
                self.queue_display,
                text="  📭 No WAV audio in queue",
                text_color="gray",
                font=ctk.CTkFont(size=11, slant="italic")
            )
            empty_label.pack(pady=5, anchor="w")

        ctk.CTkFrame(self.queue_display, height=2, fg_color="gray30").pack(fill="x", pady=10)

        # Thumbnails
        jpg_header = ctk.CTkLabel(
            self.queue_display,
            text="🖼️ Thumbnails",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1f6aa5"
        )
        jpg_header.pack(pady=(5, 5), anchor="w")

        if self.download_queue.thumbnail_queue:
            for link in self.download_queue.thumbnail_queue:
                self._create_queue_item(
                    f"Thumbnail: {link[:60]}...",
                    lambda l=link: self._remove_thumbnail(l)
                )
        else:
            empty_label = ctk.CTkLabel(
                self.queue_display,
                text="  📭 No thumbnails in queue",
                text_color="gray",
                font=ctk.CTkFont(size=11, slant="italic")
            )
            empty_label.pack(pady=5, anchor="w")

        ctk.CTkFrame(self.queue_display, height=2, fg_color="gray30").pack(fill="x", pady=10)

        # Tags
        tags_header = ctk.CTkLabel(
            self.queue_display,
            text="🏷️ Tags",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1f6aa5"
        )
        tags_header.pack(pady=(5, 5), anchor="w")

        if self.download_queue.tags_queue:
            for link in self.download_queue.tags_queue:
                self._create_queue_item(
                    f"Tags: {link[:60]}...",
                    lambda l=link: self._remove_tags(l)
                )
        else:
            empty_label = ctk.CTkLabel(
                self.queue_display,
                text="  📭 No tags in queue",
                text_color="gray",
                font=ctk.CTkFont(size=11, slant="italic")
            )
            empty_label.pack(pady=5, anchor="w")

    def _create_queue_item(self, text: str, remove_callback):
        item_frame = ctk.CTkFrame(self.queue_display, fg_color="transparent")
        item_frame.pack(fill="x", pady=3, padx=20)

        label = ctk.CTkLabel(
            item_frame,
            text=text,
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        label.pack(side="left", fill="x", expand=True)

        remove_btn = ctk.CTkButton(
            item_frame,
            text="❌",
            width=30,
            height=25,
            fg_color="darkred",
            hover_color="red",
            command=lambda: self._remove_and_refresh(remove_callback)
        )
        remove_btn.pack(side="right")

    def _remove_and_refresh(self, callback):
        callback()
        self.refresh_queue_display()

    def _remove_video(self, link: str, quality: int):
        if link in self.download_queue.videos_queue:
            if quality in self.download_queue.videos_queue[link]:
                self.download_queue.videos_queue[link].remove(quality)
                if not self.download_queue.videos_queue[link]:
                    del self.download_queue.videos_queue[link]

    def _remove_mp3(self, link: str):
        if link in self.download_queue.mp3_queue:
            self.download_queue.mp3_queue.remove(link)

    def _remove_wav(self, link: str):
        if link in self.download_queue.wav_queue:
            self.download_queue.wav_queue.remove(link)

    def _remove_thumbnail(self, link: str):
        if link in self.download_queue.thumbnail_queue:
            self.download_queue.thumbnail_queue.remove(link)

    def _remove_tags(self, link: str):
        if link in self.download_queue.tags_queue:
            self.download_queue.tags_queue.remove(link)

    def start_queue(self, queue_type: str):
        queue_map = {
            "mp4": self.download_queue.videos_queue,
            "mp3": self.download_queue.mp3_queue,
            "wav": self.download_queue.wav_queue,
            "jpg": self.download_queue.thumbnail_queue,
            "csv": self.download_queue.tags_queue,
        }

        if queue_type not in queue_map:
            self.status_label.configure(text="❌ Invalid queue type")
            return

        current_queue = queue_map[queue_type]

        is_empty = (
            not current_queue
            if queue_type != "mp4"
            else not any(current_queue.values())
        )

        if is_empty:
            self.status_label.configure(
                text=f"❌ {queue_type.upper()} queue is empty. Add items first!"
            )
            return

        self.status_label.configure(text=f"⏳ Starting {queue_type.upper()} downloads...")

        async def run():
            result = await self.download_queue.start_queue(queue_type)
            self.status_label.configure(text=f"✅ {result}")
            self.refresh_queue_display()

        def execute():
            asyncio.run(run())

        thread = threading.Thread(target=execute, daemon=True)
        thread.start()

    def clear_all_queues(self):
        self.download_queue.videos_queue = {}
        self.download_queue.mp3_queue = []
        self.download_queue.wav_queue = []
        self.download_queue.thumbnail_queue = []
        self.download_queue.tags_queue = []
        self.refresh_queue_display()
        self.status_label.configure(text="✅ All queues cleared")
