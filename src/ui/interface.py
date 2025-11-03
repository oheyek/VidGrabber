import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel


class AppUI(ctk.CTk):
    test: CTkLabel
    main_frame: CTkFrame

    def __init__(self) -> None:
        """
        Class of the app interface.
        """
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title("VidGrabber (v0.1)")
        self.geometry("500x280")
        self.resizable(True, True)
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)
        self.test = ctk.CTkLabel(self.main_frame, text="VidGrabber UI test", font=ctk.CTkFont(size=14, weight="bold"))
        self.test.pack(pady=(10,5))
