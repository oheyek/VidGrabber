import json
from pathlib import Path
from typing import Dict, Any


class PathManager:
    DEFAULT_EXTENSIONS = ["mp4", "mp3", "wav", "jpg", "tags"]

    def __init__(self) -> None:
        """Constructor of a PathManager class."""
        self.settings_dir = Path.home() / "Documents" / "VidGrabber"
        self.settings_file = self.settings_dir / "settings.json"
        self._ensure_settings_file()
        self.paths = self.load_settings()

    def _ensure_settings_file(self) -> None:
        """Ensure settings directory and file exist."""
        self.settings_dir.mkdir(parents=True, exist_ok=True)

        # Remove if it's a directory instead of file
        if self.settings_file.exists() and self.settings_file.is_dir():
            import shutil
            shutil.rmtree(self.settings_file)

        # Create with defaults if doesn't exist or is empty
        if not self.settings_file.exists() or self.settings_file.stat().st_size == 0:
            self._write_default_settings()

    def _write_default_settings(self) -> None:
        """Write default download paths to settings file."""
        defaults: dict[str, str] = {
            ext: str(Path.home() / "Downloads" / ext)
            for ext in self.DEFAULT_EXTENSIONS
        }

        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(defaults, f, ensure_ascii=False, indent=4)

    def load_settings(self) -> Dict[str, Path]:
        """
        Load settings from file and ensure directories exist.
        :return: Dictionary mapping extensions to Path objects.
        """
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError, FileNotFoundError):
            self._write_default_settings()
            return self.load_settings()

        if not data:
            self._write_default_settings()
            return self.load_settings()

        # Convert to Path objects and create directories
        paths: dict[Any, Any] = {}
        for key, value in data.items():
            path = Path(value)
            path.mkdir(parents=True, exist_ok=True)
            paths[key] = path

        return paths

    def get_download_path(self, ext: str) -> Path:
        """
        Get download path for extension, creating it if necessary.
        Thread-safe implementation for concurrent downloads.
        :param ext: File extension (without dot)
        :return: Path object for the download directory
        """
        if ext not in self.paths:
            # Create fallback path
            fallback = Path.home() / "Downloads" / ext
            self.paths[ext] = fallback

        # Ensure directory exists (thread-safe with exist_ok=True)
        try:
            self.paths[ext].mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            pass

        return self.paths[ext]

    @staticmethod
    def ensure_parent(file_path: Path) -> None:
        """
        Ensure parent directory exists for a file path.

        :param file_path: Path to a file
        """
        file_path.parent.mkdir(parents=True, exist_ok=True)

    def save_settings(self) -> None:
        """
        Save current paths to settings file.
        """
        data = {key: str(path) for key, path in self.paths.items()}
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)