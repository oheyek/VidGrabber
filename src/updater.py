import subprocess
import sys
from typing import Optional


def update_yt_dlp() -> Optional[str]:
    """
    Updates yt-dlp to the latest version.
    :return: Update status message.
    """
    try:
        print("Checking for updates yt-dlp...")

        uv_check = subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            text=True
        )

        if uv_check.returncode == 0:
            result = subprocess.run(
                ["uv", "pip", "install", "--upgrade", "yt-dlp"],
                capture_output=True,
                text=True,
                timeout=30
            )
        else:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
                capture_output=True,
                text=True,
                timeout=30
            )

        if result.returncode == 0:
            if "Successfully installed" in result.stdout:
                print("✓ yt-dlp successfully updated!")
                return "updated"
            else:
                print("✓ yt-dlp is now available in its latest version")
                return "already_latest"
        else:
            print(f"⚠ Update error: {result.stderr}")
            return "error"

    except subprocess.TimeoutExpired:
        print("⚠ The update timeout has been exceeded.")
        return "timeout"
    except Exception as e:
        print(f"⚠ Failed to update yt-dlp: {e}")
        return "error"


def check_yt_dlp_version() -> Optional[str]:
    """
    Checks the current version yt-dlp.
    :return: Version yt-dlp or None in case of error.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"Current version of yt-dlp: {version}")
            return version
        return None
    except Exception as e:
        print(f"Unable to check version: {e}")
        return None