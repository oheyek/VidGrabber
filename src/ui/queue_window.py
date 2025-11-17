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
        header = ctk.CTkLabel(main_container, text="Download Queue", font=ctk.CTkFont(size=20, weight="bold"))
        header.pack(pady=(10, 15))

        self.queue_frame = ctk.CTkScrollableFrame(
            main_container,
            width=850,
            height=450,
            fg_color="transparent"
        )
        self.queue_frame.pack(pady=10, padx=10, fill="both", expand=True)

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

        self.clear_btn = ctk.CTkButton(
            self.controls_frame,
            text="🗑️ Clear All",
            width=120,
            fg_color="red",
            hover_color="darkred",
            command=self.clear_all_queues
        )
        self.clear_btn.pack(side="right", padx=5)

        self.refresh_btn = ctk.CTkButton(
            self.controls_frame,
            text="🔄 Refresh",
            width=100,
            command=self.refresh_queue_display
        )
        self.refresh_btn.pack(side="right", padx=5)

        # Status label
        self.status_label = ctk.CTkLabel(
            main_container,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=5)

        self.refresh_queue_display()

    def refresh_queue_display(self):
        for widget in self.queue_frame.winfo_children():
            widget.destroy()

        if self.download_queue.videos_queue:
            self._create_section_header("🎬 Video Queue (MP4)")
            for link, qualities in self.download_queue.videos_queue.items():
                for quality in qualities:
                    item = QueueItem(
                        self.queue_frame,
                        link,
                        "mp4",
                        quality,
                        lambda l=link, q=quality: self.remove_video(l, q)
                    )
                    item.pack(fill="x", pady=3, padx=10)

        if self.download_queue.mp3_queue:
            self._create_section_header("🎵 Audio Queue (MP3)")
            for link in self.download_queue.mp3_queue:
                item = QueueItem(
                    self.queue_frame,
                    link,
                    "mp3",
                    None,
                    lambda l=link: self.remove_mp3(l)
                )
                item.pack(fill="x", pady=3, padx=10)

        if self.download_queue.wav_queue:
            self._create_section_header("🎵 Audio Queue (WAV)")
            for link in self.download_queue.wav_queue:
                item = QueueItem(
                    self.queue_frame,
                    link,
                    "wav",
                    None,
                    lambda l=link: self.remove_wav(l)
                )
                item.pack(fill="x", pady=3, padx=10)

        if self.download_queue.thumbnail_queue:
            self._create_section_header("🖼️ Thumbnail Queue")
            for link in self.download_queue.thumbnail_queue:
                item = QueueItem(
                    self.queue_frame,
                    link,
                    "jpg",
                    None,
                    lambda l=link: self.remove_thumbnail(l)
                )
                item.pack(fill="x", pady=3, padx=10)

        if self.download_queue.tags_queue:
            self._create_section_header("🏷️ Tags Queue")
            for link in self.download_queue.tags_queue:
                item = QueueItem(
                    self.queue_frame,
                    link,
                    "csv",
                    None,
                    lambda l=link: self.remove_tags(l)
                )
                item.pack(fill="x", pady=3, padx=10)

        if not any([
            self.download_queue.videos_queue,
            self.download_queue.mp3_queue,
            self.download_queue.wav_queue,
            self.download_queue.thumbnail_queue,
            self.download_queue.tags_queue
        ]):
            empty_label = ctk.CTkLabel(
                self.queue_frame,
                text="📭 Queue is empty",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            )
            empty_label.pack(pady=50)

    def _create_section_header(self, text: str):
        header = ctk.CTkLabel(
            self.queue_frame,
            text=text,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        header.pack(fill="x", pady=(15, 5), padx=10)

      