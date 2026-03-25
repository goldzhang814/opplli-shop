import redis.asyncio as aioredis
from app.config import settings

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis


# ── Key helpers ────────────────────────────────────────────────────────────────
class RedisKeys:
    # Cart
    @staticmethod
    def cart_user(user_id: int) -> str:
        return f"cart:user:{user_id}"

    @staticmethod
    def cart_guest(token: str) -> str:
        return f"cart:guest:{token}"

    # Session / rate limit
    @staticmethod
    def rate_limit(identifier: str, action: str) -> str:
        return f"rl:{action}:{identifier}"

    # Payment failed email dedup
    @staticmethod
    def payment_failed_email(order_id: int) -> str:
        return f"email:payment_failed:{order_id}"

    # Coupon lock (prevent concurrent over-redemption)
    @staticmethod
    def coupon_lock(code: str) -> str:
        return f"lock:coupon:{code}"

    # Channel session tracking
    @staticmethod
    def channel_session(session_id: str) -> str:
        return f"channel:session:{session_id}"

    # Password reset token
    @staticmethod
    def pw_reset(token: str) -> str:
        return f"pw_reset:{token}"
