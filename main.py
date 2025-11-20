import asyncio
import ctypes
import sys

from src.ui.interface import AppUI
from src.updater import initialize_binaries

if sys.platform == 'win32':
    import os

    os.environ['PYTHONIOENCODING'] = 'utf-8'

    if sys.stdout is not None:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    if sys.stderr is not None:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')


async def main() -> None:
    """
    Main function of the program.
    """
    if sys.stdout is not None:
        print("=" * 50)

    await initialize_binaries()

    if sys.stdout is not None:
        print("=" * 50)
        print()

    interface: AppUI = AppUI()
    interface.mainloop()


if __name__ == "__main__":
    if sys.platform == 'win32':
        try:
            myappid = 'vidgrabber.app.release.v1'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass
    asyncio.run(main())
