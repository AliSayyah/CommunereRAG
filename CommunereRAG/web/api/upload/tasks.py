import base64
import os

from io import BytesIO

import taskiq_fastapi
from nltk import sent_tokenize
from pdfminer.high_level import extract_text
from taskiq import TaskiqDepends

import pysqlite3
import sys

sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

from chromadb import AsyncClientAPI, EmbeddingFunction

from CommunereRAG.db.models.document_model import DocumentRecord
from CommunereRAG.services.chroma.dependency import get_chroma_client, get_ef
from CommunereRAG.tkq import broker

# Taskiq Setup
taskiq_fastapi.init(broker, "CommunereRAG.web.application:get_app")


def split_text_into_chunks(text, max_tokens=1000, language: str = "english"):
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []

    # Estimate token count per sentence (~5 characters per token on average)
    token_count = 0

    for sentence in sentences:
        sentence_tokens = len(sentence) // 5
        if token_count + sentence_tokens > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            token_count = sentence_tokens
        else:
            current_chunk.append(sentence)
            token_count += sentence_tokens

    # Add any remaining sentences
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


@broker.task
async def process_document_task(
    file_content: str,
    metadata: dict,
    chroma_client: AsyncClientAPI = TaskiqDepends(get_chroma_client),
    ef: EmbeddingFunction = TaskiqDepends(get_ef),
):
    # Extract text from file
    file_content = base64.b64decode(file_content)
    text_content = extract_text(BytesIO(file_content))

    if not text_content.strip():
        raise ValueError("Extracted document content is empty")

    chunks = split_text_into_chunks(text_content, max_tokens=1000, language=metadata["language"])

    # Store in ChromaDB
    collection = await chroma_client.get_or_create_collection(
        name="documents", embedding_function=ef
    )
    embedding_id = os.urandom(16).hex()
    await collection.add(
        documents=chunks,
        metadatas=[metadata] * len(chunks),
        ids=[embedding_id + str(i) for i in range(len(chunks))],
    )

    # Store in MongoDB
    doc_record = DocumentRecord(
        title=metadata["title"], content=text_content, embedding_id=embedding_id
    )
    await doc_record.insert()
