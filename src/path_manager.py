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
        self._paths = None

    @property
    def paths(self) -> Dict[str, Path]:
        """Lazy load paths only when needed."""
        if self._paths is None:
            self._paths = self.load_settings()
        return self._paths

    @paths.setter
    def paths(self, value: Dict[str, Path]) -> None:
        """Allow setting paths."""
        self._paths = value

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
        """Write empty settings file - no default paths until first download."""
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)

    def load_settings(self) -> Dict[str, Path]:
        """
        Load settings from file WITHOUT creating directories.
        :return: Dictionary mapping extensions to Path objects (empty if no settings).
        """
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError, FileNotFoundError):
            self._write_default_settings()
            return {}

        # Convert to Path objects WITHOUT creating directories
        paths: dict[Any, Any] = {}
        for key, value in data.items():
            paths[key] = Path(value)

        return paths

    def get_download_path(self, ext: str) -> Path:
        """
        Get download path for extension, creating it if necessary.
        Only creates folder for the requested extension.
        :param ext: File extension (without dot)
        :return: Path object for the download directory
        :raises RuntimeError: If directory cannot be created due to permissions
        """
        if ext not in self.paths:
            # Create default path ONLY for this specific extension
            fallback = Path.home() / "Downloads" / ext
            self.paths[ext] = fallback
            # Save immediately so it persists
            self.save_settings()

        # Create directory when downloading
        try:
            self.paths[ext].mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            raise RuntimeError(
                f"Cannot create directory '{self.paths[ext]}': {str(e)}. "
                f"Please check permissions or choose a different location."
            )

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