import time
from collections import defaultdict
from config import RATE_LIMIT_MESSAGES, RATE_LIMIT_WINDOW_SECONDS


class UserRateLimiter:
    """Per-user rate limiter. Prevents API budget drain from spam."""

    def __init__(self):
        self._timestamps: dict[int, list[float]] = defaultdict(list)

    def is_allowed(self, user_id: int) -> bool:
        now = time.time()
        cutoff = now - RATE_LIMIT_WINDOW_SECONDS
        self._timestamps[user_id] = [
            t for t in self._timestamps[user_id] if t > cutoff
        ]
        if len(self._timestamps[user_id]) >= RATE_LIMIT_MESSAGES:
            return False
        self._timestamps[user_id].append(now)
        return True

    def time_until_reset(self, user_id: int) -> int:
        if not self._timestamps[user_id]:
            return 0
        oldest = min(self._timestamps[user_id])
        return max(0, int(oldest + RATE_LIMIT_WINDOW_SECONDS - time.time()))


rate_limiter = UserRateLimiter()
