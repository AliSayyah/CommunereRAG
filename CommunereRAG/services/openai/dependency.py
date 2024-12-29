from typing import AsyncGenerator

from openai import AsyncOpenAI
from starlette.requests import Request
from taskiq import TaskiqDepends


async def get_openai_client(
    request: Request = TaskiqDepends(),
) -> AsyncGenerator[AsyncOpenAI, None]:  # pragma: no cover
    return request.app.state.openai_client
