"""
Retry utility with exponential backoff.
"""

import time
import logging
from functools import wraps
from typing import Callable, Type, Tuple

logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    """
    Retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum retry attempts
        delay: Initial delay between retries (seconds)
        exceptions: Exceptions to catch and retry

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            current_delay = delay

            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    logger.warning(
                        f"[Retry] Attempt {attempt}/{max_attempts} failed: {str(e)}"
                    )

                    if attempt == max_attempts:
                        logger.error("[Retry] Max attempts reached. Raising exception.")
                        raise

                    time.sleep(current_delay)
                    current_delay *= 2  # Exponential backoff
                    attempt += 1

        return wrapper

    return decorator