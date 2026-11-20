import sys
import time
import functools
import logging

logger =  logging.getLogger(__name__)

def init_logging(
        level: int = logging.INFO,
        log_file: str | None = None,
):
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers
    )



def time_logging(message: str | None = None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            logger.info(message)
            result = func(*args, **kwargs)
            elapsed  = time.perf_counter() - start
            if message:
                desc = message
            else:
                desc = f"{func.__name__}"

            logger.info(f"{desc} finished in {elapsed:.2f} seconds.")
            return result

        return wrapper
    return decorator