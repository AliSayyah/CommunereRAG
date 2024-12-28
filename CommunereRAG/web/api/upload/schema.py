from typing import List

from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    title: str
    language: str = "english"
    class Config:
        from_attributes = True
