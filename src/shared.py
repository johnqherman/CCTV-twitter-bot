import logging
import time
from functools import wraps
from typing import Callable, Tuple, Type

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def exponential_backoff(
    attempts: int, initial_delay: int, factor: int, exception_types: Tuple[Type[Exception], ...]
) -> Callable:
    """
    Decorator to retry a function with exponential backoff on specified exceptions.

    Args:
        attempts (int): Max number of attempts before finding a new camera.
        initial_delay (int): Initial delay in seconds between retries.
        factor (int): Factor to multiply delay by for each retry.
        exception_types (Tuple[Type[Exception], ...]): Exceptions to retry on.

    Returns:
        Callable: The wrapped function with exponential backoff applied.
    """

    def exponential_backoff_decorator(func: Callable) -> Callable:
        @wraps(func)  # preserve original function's metadata
        def wrapper(*args, **kwargs):
            delay = initial_delay  # set initial delay
            for attempt in range(1, attempts):
                try:
                    # call original function with given arguments
                    return func(*args, **kwargs)
                except exception_types as e:
                    # if last attempt, log error
                    if attempt == attempts - 1:
                        logger.error(e)

                    # otherwise, log warning and retry after delay
                    logger.info(f"retrying in {delay} seconds... (attempt {attempt + 1})")
                    time.sleep(delay)
                    delay *= factor

        return wrapper  # return wrapped function

    return exponential_backoff_decorator  # return decorator
