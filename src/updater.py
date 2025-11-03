import asyncio
import os
import platform
import sys
import socket
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


def is_internet_available(timeout: float = 10.0) -> bool:
    """
    Quick check for internet connectivity via HTTP request.
    """
    import urllib.request

    urls = ["https://www.google.com", "https://www.cloudflare.com", "https://1.1.1.1"]

    for url in urls:
        try:
            req = urllib.request.Request(url, method="HEAD")
            urllib.request.urlopen(req, timeout=timeout)
            return True
        except Exception:
            continue

    return False


def check_file_or_exit(path: Path, name: str) -> None:
    """
    Ensure that the given binary exists and is executable (where applicable).
    Exit the program immediately on failure.
    """
    if not path.exists():
        print(f"Error: {name} not found at {path}")
        sys.exit(1)

    if platform.system().lower() != "windows":
        if not os.access(path, os.X_OK):
            try:
                ensure_executable(path)
            except Exception:
                print(f"Error: {name} at {path} is not executable and permissions couldn't be changed.")
                sys.exit(1)
        if not os.access(path, os.X_OK):
            print(f"Error: {name} at {path} is not executable.")
            sys.exit(1)


async def check_yt_dlp_version() -> str:
    """
    Function to check current yt-dlp version.
    :return: Current version of yt-dlp.
    """
    try:
        yt_dlp_path = get_yt_dlp_path()
        ensure_executable(yt_dlp_path)

        process = await asyncio.create_subprocess_exec(
            str(yt_dlp_path), "--version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()

        version = stdout.decode().strip()
        print(f"Current yt-dlp version: {version}")
        return version
    except Exception as e:
        print(f"Error while checking yt-dlp version: {e}")
        return ""


async def update_yt_dlp() -> bool:
    """
    Function to update yt-dlp to the latest version.
    :return: Bool value whether yt-dlp has been updated.
    """
    try:
        yt_dlp_path = get_yt_dlp_path()
        ensure_executable(yt_dlp_path)
        print("Getting yt-dlp update...")

        process = await asyncio.create_subprocess_exec(
            str(yt_dlp_path), "-U",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()

        output = stdout.decode()
        if "up to date" in output.lower() or "up-to-date" in output.lower():
            print("yt-dlp is up to date.")
        else:
            print("yt-dlp has been updated.")
        return True
    except Exception as e:
        print(f"Error during yt-dlp update: {e}")
        return False


async def verify_ffmpeg() -> bool:
    """
    Function to verify whether ffmpeg is available.
    :return: Bool value whether ffmpeg is available.
    """
    try:
        ffmpeg_path = get_ffmpeg_path()
        ensure_executable(ffmpeg_path)

        process = await asyncio.create_subprocess_exec(
            str(ffmpeg_path), "-version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()

        print("ffmpeg is available.")
        return True
    except Exception:
        print(f"Warning: ffmpeg not found in {get_ffmpeg_path()}")
        return False


async def initialize_binaries() -> None:
    """
    Initialize and verify all binaries in parallel.
    Exits the program immediately if prerequisites are not met.
    """
    # Synchronous prerequisite checks that terminate the program on failure
    if not is_internet_available():
        print("Error: No internet connection detected. Exiting.")
        sys.exit(1)

    try:
        check_file_or_exit(get_yt_dlp_path(), "yt-dlp")
        check_file_or_exit(get_ffmpeg_path(), "ffmpeg")
    except OSError as e:
        print(f"Error determining binaries directory: {e}")
        sys.exit(1)

    # Proceed with async verification and updates
    await asyncio.gather(
        check_yt_dlp_version(),
        verify_ffmpeg()
    )
    await update_yt_dlp()
