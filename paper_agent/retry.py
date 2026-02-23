"""
Retry Module - Exponential backoff retry logic for LLM calls.
"""
import time
from typing import Callable, Any, Optional, Type, Tuple
from functools import wraps


class RetryError(Exception):
    """Exception raised when all retry attempts are exhausted."""

    def __init__(self, message: str, attempts: int, last_exception: Optional[Exception]):
        super().__init__(message)
        self.attempts = attempts
        self.last_exception = last_exception


def retry_on_exception(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[int, Exception], None]] = None
):
    """
    Decorator for retrying a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each retry
        max_delay: Maximum delay in seconds
        exceptions: Tuple of exception types to catch and retry on
        on_retry: Optional callback function called on each retry (attempt, exception)

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            delay = initial_delay

            for attempt in range(max_retries + 1):  # +1 for the initial attempt
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    # If this was the last attempt, raise
                    if attempt >= max_retries:
                        raise RetryError(
                            f"Function {func.__name__} failed after {max_retries} retries",
                            max_retries,
                            last_exception
                        ) from last_exception

                    # Call on_retry callback if provided
                    if on_retry:
                        on_retry(attempt + 1, e)

                    # Calculate delay with exponential backoff
                    delay = min(delay * backoff_factor, max_delay)

                    # Wait before retrying
                    time.sleep(delay)

        return wrapper
    return decorator


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(self,
                 max_retries: int = 3,
                 initial_delay: float = 1.0,
                 backoff_factor: float = 2.0,
                 max_delay: float = 60.0):
        """
        Initialize retry configuration.

        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            backoff_factor: Multiplier for delay after each retry
            max_delay: Maximum delay in seconds
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay

    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay for a given attempt.

        Args:
            attempt: Retry attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        delay = self.initial_delay * (self.backoff_factor ** attempt)
        return min(delay, self.max_delay)


# Default retry configuration
DEFAULT_RETRY_CONFIG = RetryConfig()