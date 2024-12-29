import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import beanie
import chromadb
from chromadb.utils import embedding_functions
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from prometheus_fastapi_instrumentator.instrumentation import (
    PrometheusFastApiInstrumentator,
)

from CommunereRAG.db.models import load_all_models
from CommunereRAG.services.redis.lifespan import init_redis, shutdown_redis
from CommunereRAG.settings import settings
from CommunereRAG.tkq import broker
from openai import AsyncOpenAI


async def _setup_db(app: FastAPI) -> None:
    client = AsyncIOMotorClient(str(settings.db_url))  # type: ignore
    app.state.db_client = client
    await beanie.init_beanie(
        database=client[settings.db_base],
        document_models=load_all_models(),  # type: ignore
    )


async def _setup_chroma(app: FastAPI) -> None:
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"), model_name="text-embedding-3-small"
    )
    client = await chromadb.AsyncHttpClient(host="chroma")
    app.state.ef = openai_ef
    app.state.chroma_client = client


def _setup_nltk(app: FastAPI) -> None:
    import nltk

    nltk.download("punkt_tab")


async def _setup_openai(app: FastAPI) -> None:
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    app.state.openai_client = client


def setup_prometheus(app: FastAPI) -> None:  # pragma: no cover
    """
    Enables prometheus integration.

    :param app: current application.
    """
    PrometheusFastApiInstrumentator(should_group_status_codes=False).instrument(
        app,
    ).expose(app, should_gzip=True, name="prometheus_metrics")


@asynccontextmanager
async def lifespan_setup(
    app: FastAPI,
) -> AsyncGenerator[None, None]:  # pragma: no cover
    """
    Actions to run on application startup.

    This function uses fastAPI app to store data
    in the state, such as db_engine.

    :param app: the fastAPI application.
    :return: function that actually performs actions.
    """

    app.middleware_stack = None
    if not broker.is_worker_process:
        await broker.startup()
    await _setup_db(app)
    await _setup_chroma(app)
    await _setup_openai(app)
    _setup_nltk(app)
    init_redis(app)
    setup_prometheus(app)
    app.middleware_stack = app.build_middleware_stack()

    yield
    if not broker.is_worker_process:
        await broker.shutdown()
    await shutdown_redis(app)
