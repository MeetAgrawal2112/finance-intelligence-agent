# app/services/cache_service.py
"""
Redis Cache Service.
DB queries cache karo — response time 10x faster.
"""

import redis
import json
import os
from typing import Any, Optional
from datetime import timedelta
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """
    Redis cache wrapper.
    Key-value store with TTL (Time To Live).

    TTL Strategy:
    - Dashboard summary: 5 min (changes frequently)
    - Category analytics: 15 min
    - Forecast: 1 hour (model predictions stable)
    - User profile: 30 min
    """
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self):
        """Redis se connect karo."""
        try:
            self._client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=3,
                socket_timeout=3,
            )
            self._client.ping()
            print("✅ Redis cache connected")
            return True
        except Exception as e:
            print(f"⚠️  Redis not available: {e}")
            print("   Running without cache — slower but functional")
            self._client = None
            return False

    def get(self, key: str) -> Optional[Any]:
        """
        Cache se value lo.
        Returns None agar:
        - Key exist nahi karta
        - Redis band hai
        - Value expire ho gayi
        """
        if not self._client:
            return None
        try:
            value = self._client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int = 300
    ) -> bool:
        """
        Cache mein value save karo.
        ttl_seconds ke baad automatically expire hoga.
        """
        if not self._client:
            return False
        try:
            serialized = json.dumps(value, default=str)
            self._client.setex(key, ttl_seconds, serialized)
            return True
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Specific key delete karo."""
        if not self._client:
            return False
        try:
            self._client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        Pattern se matching sab keys delete karo.
        Example: delete_pattern("user:abc123:*")
        Yeh user ke sab cached data clear karega.
        """
        if not self._client:
            return 0
        try:
            keys = self._client.keys(pattern)
            if keys:
                return self._client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache delete pattern error: {e}")
            return 0

    def invalidate_user_cache(self, user_id: str):
        """
        Naya transaction aane pe user ka sab cache clear karo.
        Stale data se bachao.
        """
        patterns = [
            f"user:{user_id}:*",
            f"summary:{user_id}:*",
            f"analytics:{user_id}:*",
        ]
        total = 0
        for pattern in patterns:
            total += self.delete_pattern(pattern)
        logger.info(f"Cleared {total} cache keys for user {user_id}")
        return total

    @property
    def is_connected(self) -> bool:
        if not self._client:
            return False
        try:
            self._client.ping()
            return True
        except:
            return False

    def get_stats(self) -> dict:
        """Cache statistics."""
        if not self._client:
            return {"connected": False}
        try:
            info = self._client.info()
            return {
                "connected": True,
                "used_memory": info.get("used_memory_human"),
                "total_keys": self._client.dbsize(),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
            }
        except:
            return {"connected": False}


# Global instance
cache = CacheService()