"""
Rate limiter implementation using token bucket algorithm

This module provides a thread-safe rate limiter for controlling API request rates
to prevent hitting TikTok Shop API rate limits.
"""
import time
import threading
from typing import Optional


class RateLimiter:
    """
    Token bucket rate limiter for API request throttling

    This class implements the token bucket algorithm to control the rate of API requests.
    It maintains a bucket of tokens that refills at a constant rate. Each API request
    consumes a token, and requests are blocked when no tokens are available.

    The token bucket algorithm allows for burst requests up to the bucket capacity
    while maintaining an average request rate over time.

    Attributes:
        requests_per_second: Maximum number of requests allowed per second
        bucket_capacity: Maximum number of tokens the bucket can hold
        tokens: Current number of available tokens
        last_refill_time: Timestamp of the last token refill
        lock: Thread lock for thread-safe operations

    Thread Safety:
        This class is thread-safe and can be shared across multiple threads.
    """

    def __init__(
        self,
        requests_per_second: float,
        bucket_capacity: Optional[int] = None
    ):
        """
        Initialize the rate limiter with token bucket algorithm

        Args:
            requests_per_second: Maximum number of requests allowed per second.
                                Must be greater than 0.
            bucket_capacity: Maximum number of tokens the bucket can hold.
                           If None, defaults to requests_per_second.
                           This allows for burst requests up to this limit.

        Raises:
            ValueError: If requests_per_second is not positive

        Example:
            >>> # Allow 10 requests per second with burst capacity of 20
            >>> limiter = RateLimiter(requests_per_second=10, bucket_capacity=20)
            >>> limiter.acquire()  # Consumes a token

            >>> # Allow 5 requests per second with default burst capacity
            >>> limiter = RateLimiter(requests_per_second=5)
            >>> limiter.acquire()  # Consumes a token
        """
        if requests_per_second <= 0:
            raise ValueError("requests_per_second must be greater than 0")

        self.requests_per_second = requests_per_second
        self.bucket_capacity = bucket_capacity if bucket_capacity is not None else int(requests_per_second)
        self.tokens = float(self.bucket_capacity)
        self.last_refill_time = time.time()
        self.lock = threading.Lock()

    def _refill_tokens(self) -> None:
        """
        Refill tokens based on time elapsed since last refill

        This method calculates how many tokens should be added to the bucket
        based on the configured refill rate and time elapsed. It ensures the
        bucket never exceeds its maximum capacity.

        This is called internally before each acquire() operation.
        """
        current_time = time.time()
        time_elapsed = current_time - self.last_refill_time

        # Calculate tokens to add based on elapsed time and refill rate
        tokens_to_add = time_elapsed * self.requests_per_second

        # Add tokens but don't exceed bucket capacity
        self.tokens = min(self.bucket_capacity, self.tokens + tokens_to_add)

        # Update last refill time
        self.last_refill_time = current_time

    def acquire(self, tokens: int = 1, blocking: bool = True) -> bool:
        """
        Acquire tokens from the bucket

        This method attempts to consume the specified number of tokens from the bucket.
        If blocking is True and insufficient tokens are available, it will wait until
        enough tokens are available. If blocking is False, it returns immediately.

        Args:
            tokens: Number of tokens to acquire (default: 1)
            blocking: If True, wait until tokens are available. If False, return
                     immediately with success/failure status.

        Returns:
            True if tokens were successfully acquired, False otherwise (only when blocking=False)

        Raises:
            ValueError: If tokens is not positive

        Example:
            >>> limiter = RateLimiter(requests_per_second=10)
            >>>
            >>> # Blocking acquisition (waits if needed)
            >>> limiter.acquire()
            >>> # Make API request here
            >>>
            >>> # Non-blocking acquisition
            >>> if limiter.acquire(blocking=False):
            >>>     # Make API request
            >>> else:
            >>>     # Handle rate limit
        """
        if tokens <= 0:
            raise ValueError("tokens must be greater than 0")

        with self.lock:
            self._refill_tokens()

            # If we have enough tokens, consume them immediately
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True

            # If non-blocking, return False immediately
            if not blocking:
                return False

        # Blocking mode: wait until we have enough tokens
        while True:
            with self.lock:
                self._refill_tokens()

                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return True

                # Calculate how long to wait for enough tokens
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.requests_per_second

            # Sleep for the calculated wait time
            # Use a small buffer to account for timing precision
            time.sleep(wait_time)

    def get_available_tokens(self) -> float:
        """
        Get the current number of available tokens

        This method refills the bucket and returns the current token count.
        Useful for monitoring or debugging rate limiter state.

        Returns:
            Current number of available tokens

        Example:
            >>> limiter = RateLimiter(requests_per_second=10)
            >>> available = limiter.get_available_tokens()
            >>> print(f"Available tokens: {available}")
        """
        with self.lock:
            self._refill_tokens()
            return self.tokens

    def reset(self) -> None:
        """
        Reset the rate limiter to its initial state

        This method refills the bucket to maximum capacity and resets the
        refill timestamp. Useful for testing or when you need to clear
        the rate limiter state.

        Example:
            >>> limiter = RateLimiter(requests_per_second=10)
            >>> limiter.acquire()
            >>> limiter.reset()  # Bucket is now full again
        """
        with self.lock:
            self.tokens = float(self.bucket_capacity)
            self.last_refill_time = time.time()
