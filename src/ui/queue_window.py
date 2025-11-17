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