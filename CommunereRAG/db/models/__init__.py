"""CommunereRAG models."""

from typing import Sequence, Type

from beanie import Document

from CommunereRAG.db.models.document_model import DocumentRecord
from CommunereRAG.db.models.query_model import QueryLog


def load_all_models() -> Sequence[Type[Document]]:
    """Load all models from this folder."""
    return [DocumentRecord, QueryLog]
