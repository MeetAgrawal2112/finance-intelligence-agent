# app/utils/cache_decorator.py
"""
Cache decorator — ek line mein caching add karo.

Usage:
@cached(ttl=300, key_prefix="summary")
def get_monthly_summary(user_id, month, year):
    # DB query
    ...
"""

import functools
from app.services.cache_service import cache

def cached(ttl: int = 300, key_prefix: str = "cache"):
    """
    Function result cache karo.

    Args:
        ttl: Seconds mein cache lifetime
        key_prefix: Cache key ka prefix

    Example:
        @cached(ttl=300, key_prefix="monthly_summary")
        def get_summary(user_id: str, month: int, year: int):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Cache key banao — function args se
            key_parts = [key_prefix] + [str(a) for a in args] + \
                       [f"{k}:{v}" for k, v in sorted(kwargs.items())]
            cache_key = ":".join(key_parts)

            # Cache check karo
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Cache miss — function call karo
            result = func(*args, **kwargs)

            # Result cache karo
            if result is not None:
                cache.set(cache_key, result, ttl)

            return result
        return wrapper
    return decorator