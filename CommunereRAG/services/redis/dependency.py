from typing import AsyncGenerator

from fastapi import Depends
from redis.asyncio import Redis
from starlette.requests import Request
from taskiq import TaskiqDepends


async def get_redis_pool(
    request: Request = TaskiqDepends(),
) -> AsyncGenerator[Redis, None]:  # pragma: no cover
    """
    Returns connection pool.
    """
    return request.app.state.redis_pool
