from typing import Any

import taskiq_fastapi
from taskiq import (
    AsyncBroker,
    AsyncResultBackend,
    InMemoryBroker,
    SimpleRetryMiddleware,
)
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from CommunereRAG.settings import settings

result_backend: AsyncResultBackend[Any] = RedisAsyncResultBackend(
    redis_url=str(settings.redis_url.with_path("/1")),
)
broker: AsyncBroker = (
    ListQueueBroker(
        str(settings.redis_url.with_path("/1")),
    )
    .with_result_backend(result_backend)
    .with_middlewares(
        SimpleRetryMiddleware(default_retry_count=3),
    )
)

if settings.environment.lower() == "pytest":
    broker = InMemoryBroker()

taskiq_fastapi.init(
    broker,
    "CommunereRAG.web.application:get_app",
)
