import asyncio
import threading

import customtkinter as ctk

from src.queue.download_queue import DownloadQueue


class QueueWindow(ctk.CTkToplevel):
    def __init__(self, parent, download_queue: DownloadQueue):
        super().__init__(parent)
        self.download_queue = download_queue

        self.title("Queue Manager")
        self.geometry("600x700")
        self.resizable(False, False)

        self.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        window_width = 600
        window_height = 700

        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        title_label = ctk.CTkLabel(
            self,
            text="📋 Queue Manager",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(15, 10))

        self.queue_display = ctk.CTkScrollableFrame(
            self,
            width=550,
            height=450,
            fg_color="transparent"
        )
        self.queue_display.pack(pady=10, padx=20, fill="both", expand=True)

        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        self.status_label.pack(pady=5)

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=10)

        self.start_all_btn = ctk.CTkButton(
            button_frame,
            text="▶️ Start All Queues",
            width=150,
            height=35,
            command=lambda: self.start_all_queues(),
            fg_color="#1f6aa5",
            hover_color="#165a8e"
        )
        self.start_all_btn.pack(side="left", padx=5)

        self.clear_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Clear All",
            width=120,
            height=35,
            command=self.clear_all_queues,
            fg_color="#d32f2f",
            hover_color="#b71c1c"
        )
        self.clear_btn.pack(side="left", padx=5)

        self.refresh_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Refresh",
            width=100,
            height=35,
            command=self.refresh_queue_display,
            fg_color="gray40",
            hover_color="gray30"
        )
        self.refresh_btn.pack(side="left", padx=5)

        self.refresh_queue_display()

    def refresh_queue_display(self):
        for widget in self.queue_display.winfo_children():
            widget.destroy()

        # MP4 Videos
        self._create_section_header("🎬 MP4 Videos")
        if self.download_queue.videos_queue:
            for link, qualities in self.download_queue.videos_queue.items():
                for quality in qualities:
                    self._create_queue_item(
                        f"  • {link[:50]}... ({quality}p)",
                        lambda l=link, q=quality: self._remove_and_refresh(
                            lambda: self._remove_video(l, q)
                        )
                    )
        else:
            self._create_empty_label()

        self._create_separator()

        # MP3 Audio
        self._create_section_header("🎵 MP3 Audio")
        if self.download_queue.mp3_queue:
            for link in self.download_queue.mp3_queue:
                self._create_queue_item(
                    f"  • {link[:60]}...",
                    lambda l=link: self._remove_and_refresh(
                        lambda: self._remove_mp3(l)
                    )
                )
        else:
            self._create_empty_label()

        self._create_separator()

        # WAV Audio
        self._create_section_header("🎵 WAV Audio")
        if self.download_queue.wav_queue:
            for link in self.download_queue.wav_queue:
                self._create_queue_item(
                    f"  • {link[:60]}...",
                    lambda l=link: self._remove_and_refresh(
                        lambda: self._remove_wav(l)
                    )
                )
        else:
            self._create_empty_label()

        self._create_separator()

        # Thumbnails
        self._create_section_header("🖼️ Thumbnails")
        if self.download_queue.thumbnail_queue:
            for link in self.download_queue.thumbnail_queue:
                self._create_queue_item(
                    f"  • {link[:60]}...",
                    lambda l=link: self._remove_and_refresh(
                        lambda: self._remove_thumbnail(l)
                    )
                )
        else:
            self._create_empty_label()

        self._create_separator()

        # Tags
        self._create_section_header("🏷️ Tags")
        if self.download_queue.tags_queue:
            for link in self.download_queue.tags_queue:
                self._create_queue_item(
                    f"  • {link[:60]}...",
                    lambda l=link: self._remove_and_refresh(
                        lambda: self._remove_tags(l)
                    )
                )
        else:
            self._create_empty_label()

    def _create_section_header(self, text: str):
        header = ctk.CTkLabel(
            self.queue_display,
            text=text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="gray70"
        )
        header.pack(pady=(5, 5), anchor="w")

    def _create_empty_label(self):
        empty_label = ctk.CTkLabel(
            self.queue_display,
            text="  📭 No items in queue",
            text_color="gray50",
            font=ctk.CTkFont(size=11, slant="italic")
        )
        empty_label.pack(pady=5, anchor="w")

    def _create_separator(self):
        ctk.CTkFrame(
            self.queue_display,
            height=1,
            fg_color="gray30"
        ).pack(fill="x", pady=8)

    def _create_queue_item(self, text: str, remove_callback):
        item_frame = ctk.CTkFrame(self.queue_display, fg_color="transparent")
        item_frame.pack(fill="x", pady=2)

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
            command=remove_callback,
            fg_color="transparent",
            hover_color="#d32f2f"
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

    def start_all_queues(self):

        queues_to_start = []

        if self.download_queue.videos_queue:
            queues_to_start.append("mp4")
        if self.download_queue.mp3_queue:
            queues_to_start.append("mp3")
        if self.download_queue.wav_queue:
            queues_to_start.append("wav")
        if self.download_queue.thumbnail_queue:
            queues_to_start.append("jpg")
        if self.download_queue.tags_queue:
            queues_to_start.append("csv")

        if not queues_to_start:
            self.status_label.configure(text="❌ All queues are empty")
            return

        self.status_label.configure(text=f"⏳ Starting {len(queues_to_start)} queue(s)...")
        self.start_all_btn.configure(state="disabled")

        async def run():
            for queue_type in queues_to_start:
                result = await self.download_queue.start_queue(queue_type)
                print(f"{queue_type.upper()}: {result}")

            self.status_label.configure(text="✅ All downloads completed!")
            self.refresh_queue_display()
            self.start_all_btn.configure(state="normal")

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
