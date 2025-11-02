import subprocess
import sys
import platform
from pathlib import Path

def get_binaries_dir() -> Path:
    """
    Function to return binaries path basing on the used system.
    :return: System path with binaries.
    """
    base_dir = Path(__file__).parent.parent / "binaries"
    system: str = platform.system().lower()

    if system == "windows":
        return base_dir / "windows"
    elif system == "darwin":
        return base_dir / "macos"
    elif system == "linux":
        return base_dir / "linux"
    else:
        raise OSError(f"Unsupported platform: {system}")