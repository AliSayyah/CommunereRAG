from typing import List

from beanie import Document


class DocumentRecord(Document):
    title: str
    content: str
    embedding_id: str  # ID reference for Chroma embedding
