import json
from typing import List, Dict

from chromadb.api.models import AsyncCollection
from openai import AsyncOpenAI


async def retrieval_agent(query: str, top_k: int, chroma_collection: AsyncCollection):
    """
    Retrieves the top_k documents from ChromaDB based on a search query.
    """
    results = await chroma_collection.query(query_texts=[query], n_results=top_k)
    documents = []
    for doc, metadata in zip(results["documents"], results["metadatas"]):
        documents.append({"content": doc, "metadata": metadata})
    return documents

async def refinement_agent(openai_client: AsyncOpenAI, query: str, context: str, model: str = "gpt-4o"):
    """
    Refines the response using the retrieved context and the LLM.

    Args:
        openai_client (AsyncOpenAI):
        query (str): The user's query.
        context (str): Retrieved documents and their metadata.
        model (str): LLM model name.

    Returns:
        str: Refined response from the LLM.
    """

    messages = [
        {"role": "system", "content": "Your task is to refine the context user sends to you based on the query. the final result should be a clean and clear text. only return the final result without extra text like 'here is your refined text:"},
        {"role": "user", "content": json.dumps({
            "query": query,
            "context": context,
        })},
        {"role": "assistant", "content": context},
    ]

    response = await openai_client.chat.completions.create(
        model=model,
        messages=messages,
    )

    return response.choices[0].message.content
