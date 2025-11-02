import subprocess
import os
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

def ensure_executable(file_path: Path):
    if platform.system().lower() != "windows":
        try:
            os.chmod(file_path, 0o755)
        except Exception as e:
            print(f"Can't modify permissions to {file_path}: {e}")

def check_yt_dlp_version() -> str:
    """
    Function to check current yt-dlp version.
    :return: Current version of yt-dlp.
    """
    try:
        yt_dlp_path = get_yt_dlp_path()
        ensure_executable(yt_dlp_path)
        result = subprocess.run([str(yt_dlp_path), "--version"],
                                capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        print(f"Current yt-dlp version: {version}")
        return version
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error while checking yt-dlp version: {e}")
        return ""

def update_yt_dlp() -> bool:
    """
    Function to update yt-dlp to the latest version.
    :return: Bool value whether yt-dlp has been updated.
    """
    try:
        yt_dlp_path = get_yt_dlp_path()
        ensure_executable(yt_dlp_path)
        print("Getting yt-dlp update...")
        result = subprocess.run([str(yt_dlp_path), "-U"], capture_output=True, text=True, check=True)

        if "up to date" in result.stdout.lower() or "up-to-date" in result.stdout.lower():
            print("yt-dlp is up to date.")
        else:
            print("yt-dlp has been updated.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during yt-dlp update: {e}")
        return False
    except FileNotFoundError:
        print("yt-dlp not found.")
        return False

def verify_ffmpeg() -> bool:
    """
    Function to verify whether ffmpeg is available.
    :return: Bool value whether ffmpeg is available.
    """
    try:
        ffmpeg_path = get_ffmpeg_path()
        result = subprocess.run([str(ffmpeg_path), "-version"], capture_output=True, text=True, check=True)
        print("ffmpeg is available.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"Warning: ffmpeg not found in {get_ffmpeg_path()}")
        return False
