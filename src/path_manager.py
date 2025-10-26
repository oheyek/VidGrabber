import json
from pathlib import Path
import shutil
from typing import Any


class PathManager:
    def __init__(self) -> None:
        """
        Constructor of a PathManager class.
        """
        self.settings = Path.home() / "Documents" / "VidGrabber"
        self.settings_file = self.settings / "settings.json"
        self._ensure_paths()

        if self._should_apply_defaults():
            self._apply_default_settings()

    def _ensure_paths(self) -> None:
        """
        Method to check the state of the settings folder and file and create if needed.
        """
        if not self.settings.exists():
            self.settings.mkdir(parents=True, exist_ok=True)

        if self.settings_file.exists() and self.settings_file.is_dir():
            shutil.rmtree(self.settings_file)

        if not self.settings_file.exists():
            self.settings_file.touch(exist_ok=True)

    def _should_apply_defaults(self) -> bool:
        """
        Check if we need to apply default settings.
        :return: Bool value whether the file needs default settings to apply.
        """
        if self.settings_file.stat().st_size == 0:
            return True

        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return not data
        except json.JSONDecodeError:
            return True

    def _apply_default_settings(self) -> None:
        """
        Method to apply default download paths to the settings file.
        """
        self.default_download_paths: dict[str, Path] = {
            "mp4": Path.home() / "Downloads" / "mp4/",
            "mp3": Path.home() / "Downloads" / "mp3/",
            "wav": Path.home() / "Downloads" / "wav/",
            "jpg": Path.home() / "Downloads" / "jpg/",
            "tags": Path.home() / "Downloads" / "tags/",
        }

        serializable_paths = {
            key: str(value) for key, value in self.default_download_paths.items()
        }

        with open(self.settings_file, "w", encoding="utf-8") as settings:
            json.dump(
                serializable_paths, settings, ensure_ascii=False, indent=4
            )

    def load_settings(self) -> Any:
        """
        Method to load paths from a file.
        :return: The file paths dictionary.
        """
        if self.settings_file.exists() and self.settings_file.is_file():
            with open(self.settings_file, "r", encoding="utf-8") as settings:
                paths = json.load(settings)
        return paths