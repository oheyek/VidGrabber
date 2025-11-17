import asyncio
import sys

from src.ui.interface import AppUI
from src.updater import initialize_binaries

if sys.platform == 'win32':
    import os

    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


async def main() -> None:
    """
    Main function of the program.
    """
    print("=" * 50)
    await initialize_binaries()
    print("=" * 50)
    print()
    interface: AppUI = AppUI()
    interface.mainloop()


if __name__ == "__main__":
    asyncio.run(main())
