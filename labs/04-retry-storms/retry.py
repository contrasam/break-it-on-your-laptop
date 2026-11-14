"""Retry policies shared by the load generator and the api service.

RETRY=none     one attempt, no retries
RETRY=naive    retry right away on timeout or error (what most code does)
RETRY=backoff  exponential backoff with full jitter between attempts
RETRY=budget   backoff + jitter, and retries may not exceed BUDGET (10%) of requests
"""
import random


class Policy:
    def __init__(self, mode, retries, base_ms, cap_ms, budget_ratio=0.1, budget_max=10.0):
        self.mode = mode
        self.retries = 0 if mode == "none" else retries
        self.base, self.cap = base_ms / 1000, cap_ms / 1000
        self.ratio, self.max_tokens = budget_ratio, budget_max
        self.tokens = budget_max
        self.denied = 0          # retries the budget refused

    def on_request(self):
        """Every new request earns a fraction of a retry."""
        self.tokens = min(self.max_tokens, self.tokens + self.ratio)

    def may_retry(self, attempt):
        """attempt = how many attempts have already failed (1, 2, ...)."""
        if attempt > self.retries:
            return False
        if self.mode == "budget":
            if self.tokens < 1:
                self.denied += 1
                return False
            self.tokens -= 1
        return True

    def delay(self, attempt):
        """Seconds to wait before the next attempt."""
        if self.mode in ("none", "naive"):
            return 0.0
        # "Full jitter": a random wait between 0 and the exponential backoff.
        return random.uniform(0, min(self.cap, self.base * 2 ** (attempt - 1)))
