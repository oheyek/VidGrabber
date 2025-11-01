# python
# Plik: `src/log_decorator.py`
from pathlib import Path
import functools
import asyncio
import logging
from typing import Callable, Any, Coroutine

LOG_FILE = Path.cwd() / "logs.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("project_logger")
if not logger.handlers:
    handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(message)s", datefmt="%Y-%m-%dT%H:%M:%S"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def log_call(func):
    """
    A decorator that writes function calls to `logs.log`.
    Supports synchronous and asynchronous functions.
    :param func: A function to get logs from.
    :return: Wrapped function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            parts = [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
            args_str = ", ".join(parts)
        except Exception:
            args_str = "<unrepresentable args>"

        func_name = f"{func.__module__}.{func.__name__}"

        try:
            result = func(*args, **kwargs)

            if asyncio.iscoroutine(result):
                async def async_handler():
                    try:
                        res = await result
                        logger.info(f"{func_name} | args: {args_str} | result: {res!r}")
                        return res
                    except Exception:
                        logger.exception(f"{func_name} | args: {args_str} | exception")
                        raise
                return async_handler()

            logger.info(f"{func_name} | args: {args_str} | result: {result!r}")
            return result

        except Exception:
            logger.exception(f"{func_name} | args: {args_str} | exception")
            raise

    return wrapper