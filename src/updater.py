import asyncio
import os
import platform
import shutil
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from functools import lru_cache
from pathlib import Path
from urllib.request import Request


@lru_cache(maxsize=1)
def get_binaries_dir() -> Path:
    """
    Get the platform-specific binaries directory path.
    :return: Path to the platform-specific binaries directory
    """
    base_dir = Path.home() / "Documents" / "VidGrabber" / "binaries"
    base_dir.mkdir(parents=True, exist_ok=True)

    system = platform.system().lower()
    if system == "windows":
        target = base_dir / "windows"
    elif system == "darwin":
        target = base_dir / "macos"
    elif system == "linux":
        target = base_dir / "linux"
    else:
        raise OSError(f"Unsupported platform: {system}")

    target.mkdir(parents=True, exist_ok=True)
    return target


@lru_cache(maxsize=1)
def get_yt_dlp_path() -> Path:
    """
    Get the yt_dlp path.
    :return: Path to platform specific yt_dlp.
    """
    binaries_dir = get_binaries_dir()
    return binaries_dir / ("yt-dlp.exe" if platform.system().lower() == "windows" else "yt-dlp")


@lru_cache(maxsize=1)
def get_ffmpeg_path() -> Path:
    """
    Get the ffmpeg path.
    :return: Path to platform specific ffmpeg.
    """
    binaries_dir = get_binaries_dir()
    return binaries_dir / ("ffmpeg.exe" if platform.system().lower() == "windows" else "ffmpeg")


def ensure_executable(file_path: Path) -> None:
    """
    Ensures the specified file is executable on Unix-like systems, doing nothing on Windows.
    :param file_path: Path to the file to make executable.
    """
    if platform.system().lower() == "windows":
        return
    try:
        os.chmod(str(file_path), 0o755)
    except Exception as e:
        print(f"Can't modify permissions to {file_path}: {e}")


def is_internet_available(timeout: float = 10.0) -> bool:
    """
    Checks if the internet is reachable by attempting HEAD requests to common URLs within the given timeout.
    :param timeout: Maximum time in seconds to wait for each connection attempt.
    :return: True if any connection succeeds, False otherwise.
    """
    urls = ["https://www.google.com", "https://www.cloudflare.com", "https://1.1.1.1"]
    for url in urls:
        try:
            req = Request(url, method="HEAD")
            urllib.request.urlopen(req, timeout=timeout)
            return True
        except Exception:
            continue
    return False


def check_file_or_exit(path: Path, name: str) -> None:
    """
    Verifies that the specified file exists and is executable (on Unix-like systems), exiting the program with an error message if not.
    :param path: Path to the file to check.
    :param name: Human-readable name of the file for error messages.
    """
    if not path.exists():
        print(f"Error: {name} not found at {path}")
        sys.exit(1)
    if platform.system().lower() != "windows":
        ensure_executable(path)
        if not os.access(str(path), os.X_OK):
            print(f"Error: {name} at {path} is not executable.")
            sys.exit(1)


def _download(url: str, dest: Path, timeout: float = 30.0) -> None:
    """
    Downloads the content from the specified URL to the given destination path, creating parent directories if needed.
    :param url: URL of the file to download.
    :param dest: Local path where the downloaded file will be saved.
    :param timeout: Maximum time in seconds to wait for the download.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=timeout) as resp, open(dest, "wb") as out:
        shutil.copyfileobj(resp, out)


def _extract_ffmpeg_from_tar_xz(archive: Path, target: Path) -> None:
    """
    Extracts the ffmpeg executable from a .tar.xz archive to the specified target path, creating parent directories if necessary.
    :param archive: Path to the .tar.xz archive containing ffmpeg.
    :param target: Path where the extracted ffmpeg executable will be saved.
    """
    with tarfile.open(archive, mode="r:xz") as tf:
        for member in tf.getmembers():
            name = member.name.replace("\\", "/")
            if member.isfile() and name.endswith("/ffmpeg"):
                f = tf.extractfile(member)
                if f is None:
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with open(target, "wb") as out:
                    shutil.copyfileobj(f, out)
                return
    raise FileNotFoundError("ffmpeg not found inside tar.xz")


def _extract_ffmpeg_from_zip(archive: Path, target_name: str, target: Path) -> None:
    """
    Extracts the specified file from a ZIP archive to the target path, creating parent directories if needed.
    :param archive: Path to the ZIP archive.
    :param target_name: Name of the file to extract from the archive.
    :param target: Path where the extracted file will be saved.
    """
    with zipfile.ZipFile(archive, "r") as zf:
        candidates = [n for n in zf.namelist() if
                      n.endswith(f"/{target_name}") or n == target_name or n.endswith(target_name)]
        if not candidates:
            raise FileNotFoundError(f"{target_name} not found in zip")
        member = candidates[0]
        target.parent.mkdir(parents=True, exist_ok=True)
        with zf.open(member) as src, open(target, "wb") as dst:
            shutil.copyfileobj(src, dst)


def download_binaries_if_missing() -> None:
    """
    Downloads yt-dlp and ffmpeg binaries for the current platform if they are missing, storing them in the binaries directory and ensuring executability on Unix-like systems.
    """
    system = platform.system().lower()
    base = get_binaries_dir().parent
    bin_dir = get_binaries_dir()
    bin_dir.mkdir(parents=True, exist_ok=True)

    if system == "linux":
        yt_url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_linux"
        ff_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz"
        yt_path = bin_dir / "yt-dlp"
        ff_path = bin_dir / "ffmpeg"

        if not yt_path.exists():
            print("Downloading yt-dlp for linux...")
            _download(yt_url, yt_path)
            ensure_executable(yt_path)

        if not ff_path.exists():
            print("Downloading ffmpeg for linux (tar.xz)...")
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td) / "ffmpeg.tar.xz"
                _download(ff_url, tmp)
                _extract_ffmpeg_from_tar_xz(tmp, ff_path)
                ensure_executable(ff_path)

    elif system == "darwin":
        yt_url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos"
        ff_url = "https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip"
        yt_path = bin_dir / "yt-dlp"
        ff_path = bin_dir / "ffmpeg"

        if not yt_path.exists():
            print("Downloading yt-dlp for macOS...")
            _download(yt_url, yt_path)
            ensure_executable(yt_path)

        if not ff_path.exists():
            print("Downloading ffmpeg for macOS (zip)...")
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td) / "ffmpeg.zip"
                _download(ff_url, tmp)
                _extract_ffmpeg_from_zip(tmp, "ffmpeg", ff_path)
                ensure_executable(ff_path)

    elif system == "windows":
        yt_url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
        ff_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        yt_path = bin_dir / "yt-dlp.exe"
        ff_path = bin_dir / "ffmpeg.exe"

        if not yt_path.exists():
            print("Downloading yt-dlp for Windows...")
            _download(yt_url, yt_path)

        if not ff_path.exists():
            print("Downloading ffmpeg for Windows (zip)...")
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td) / "ffmpeg.zip"
                _download(ff_url, tmp)
                _extract_ffmpeg_from_zip(tmp, "ffmpeg.exe", ff_path)
    else:
        raise OSError(f"Unsupported platform: {system}")


async def check_yt_dlp_version() -> str:
    """
    Checks and returns the version of the installed yt-dlp executable, ensuring it is executable.
    :return: The current yt-dlp version as a string, or an empty string if an error occurs.
    """
    try:
        yt_dlp_path = get_yt_dlp_path()
        ensure_executable(yt_dlp_path)
        proc = await asyncio.create_subprocess_exec(str(yt_dlp_path), "--version", stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
        stdout, _ = await proc.communicate()
        version = stdout.decode().strip()
        print(f"Current yt-dlp version: {version}")
        return version
    except Exception as e:
        print(f"Error while checking yt-dlp version: {e}")
        return ""


async def update_yt_dlp() -> bool:
    """
    Updates the installed yt-dlp executable and prints whether it was already up to date or has been updated.
    :return: True if the update process ran without errors, False otherwise.
    """
    try:
        yt_dlp_path = get_yt_dlp_path()
        ensure_executable(yt_dlp_path)
        print("Getting yt-dlp update...")
        proc = await asyncio.create_subprocess_exec(str(yt_dlp_path), "-U", stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
        stdout, _ = await proc.communicate()
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
    Verifies that the ffmpeg executable is available and can be run, printing a confirmation or warning message.
    :return: True if ffmpeg is available and executable, False otherwise.
    """
    try:
        ffmpeg_path = get_ffmpeg_path()
        ensure_executable(ffmpeg_path)
        proc = await asyncio.create_subprocess_exec(str(ffmpeg_path), "-version", stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
        await proc.communicate()
        print("ffmpeg is available.")
        return True
    except Exception as e:
        print(f"Warning: ffmpeg not found in {get_ffmpeg_path()}: {e}")
        return False


async def initialize_binaries() -> None:
    """
    Ensures that yt-dlp and ffmpeg binaries are present, up to date, and executable, downloading them if missing and verifying their availability.
    """
    if not is_internet_available():
        print("Error: No internet connection detected. Exiting.")
        sys.exit(1)

    try:
        yt_dlp = get_yt_dlp_path()
        ffmpeg = get_ffmpeg_path()

        if yt_dlp.exists() and ffmpeg.exists():
            print("Binaries found — just checking the version and updating yt-dlp...")
            if platform.system().lower() != "windows":
                ensure_executable(yt_dlp)
            await check_yt_dlp_version()
            await update_yt_dlp()
            return

        try:
            download_binaries_if_missing()
        except Exception as e:
            print(f"Error downloading binaries: {e}")
            sys.exit(1)

        if platform.system().lower() != "windows":
            if yt_dlp.exists():
                ensure_executable(yt_dlp)
            if ffmpeg.exists():
                ensure_executable(ffmpeg)

        check_file_or_exit(yt_dlp, "yt-dlp")
        check_file_or_exit(ffmpeg, "ffmpeg")
    except OSError as e:
        print(f"Error determining binaries directory: {e}")
        sys.exit(1)

    await asyncio.gather(check_yt_dlp_version(), verify_ffmpeg())
    await update_yt_dlp()
