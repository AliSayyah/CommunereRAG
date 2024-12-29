from typing import AsyncGenerator

from chromadb import AsyncClientAPI, EmbeddingFunction
from starlette.requests import Request
from taskiq import TaskiqDepends


async def get_chroma_client(
    request: Request = TaskiqDepends(),
) -> AsyncGenerator[AsyncClientAPI, None]:  # pragma: no cover
    """
    Returns Chroma client.
    """
    return request.app.state.chroma_client


async def get_ef(
    request: Request = TaskiqDepends(),
) -> AsyncGenerator[EmbeddingFunction, None]:  # pragma: no cover

    return request.app.state.ef
