import asyncio

from src.ui.interface import AppUI
from src.updater import initialize_binaries

LINK = "https://youtu.be/dQw4w9WgXcQ?si=52ngrNGc_WNyEkUb"
LINK2 = "https://youtu.be/njX2bu-_Vw4?si=VgF6vfdYZFh9dhPe"
LINK3 = "https://youtu.be/xOMMV_qXcQ8?si=q5pqhGOqFbcr4acG"

import sys

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
