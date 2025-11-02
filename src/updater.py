import subprocess
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

def get_yt_dlp_path() -> Path:
    """
    Function to return the path to yt-dlp binary.
    :return: yt-dlp binary path basing on platform.
    """
    binaries_dir = get_binaries_dir()
    if platform.system().lower() == "windows":
        return binaries_dir / "yt-dlp.exe"
    return binaries_dir / "yt-dlp"

def get_ffmpeg_path() -> Path:
    """
    Function to return the path to ffmpeg binary.
    :return: ffmpeg binary path basing on platform.
    """
    binaries_dir = get_binaries_dir()
    if platform.system().lower() == "windows":
        return binaries_dir / "ffmpeg.exe"
    return binaries_dir / "ffmpeg"

def check_yt_dlp_version() -> str:
    """
    Function to check current yt-dlp version.
    :return: Current version of yt-dlp.
    """
    try:
        yt_dlp_path = get_yt_dlp_path()
        result = subprocess.run([str(yt_dlp_path), "--version"],
                                capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        print(f"Current yt-dlp version: {version}")
        return version
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error while checking yt-dlp version: {e}")
        return ""