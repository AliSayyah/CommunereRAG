import datetime

from beanie import Document
from pydantic import Field


class QueryLog(Document):
    query: str
    response: str
    context: str = ""
    timestamp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    duration: float  # in seconds

    class Settings:
        collection = "query_logs"
