import asyncio
from typing import Any

import pytest

from src.updater import initialize_binaries


@pytest.fixture(scope="session", autouse=True)
def setup_binaries() -> Any:
    """
    Automatically initializes binaries before all tests.
    Runs once per test session.
    """
    asyncio.run(initialize_binaries())
    yield
