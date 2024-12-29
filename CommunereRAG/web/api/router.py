from fastapi.routing import APIRouter

from CommunereRAG.web.api import docs, upload, echo, monitoring, query, logs

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(docs.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
