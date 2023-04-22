import logging
import time
from functools import wraps
from typing import Callable, Tuple, Type

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def exponential_backoff(
    attempts: int, initial_delay: int, factor: int, exception_types: Tuple[Type[Exception], ...]
) -> Callable:
    def exponential_backoff_decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(1, attempts):
                try:
                    return func(*args, **kwargs)
                except exception_types as e:
                    if attempt == attempts - 1:
                        logger.error(e)

                    logger.info(f"retrying in {delay} seconds... (attempt {attempt + 1})")
                    time.sleep(delay)
                    delay *= factor

        return wrapper

    return exponential_backoff_decorator
