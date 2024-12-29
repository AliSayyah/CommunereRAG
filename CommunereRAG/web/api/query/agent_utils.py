from chromadb import AsyncClientAPI, EmbeddingFunction
from openai import AsyncOpenAI
from openai.types.chat.chat_completion_message_tool_call import Function

from CommunereRAG.db.models import QueryLog
from CommunereRAG.web.api.query.agents import retrieval_agent, refinement_agent


async def run_agent_chain(tool_call: Function, openai_client: AsyncOpenAI, chroma_client: AsyncClientAPI, ef: EmbeddingFunction):
    """
    Handles the tool call logic for document retrieval and response refinement.
    """
    try:
        parameters = eval(tool_call.arguments)  # Convert JSON string to dictionary
        query_params = {
            "query": parameters["query"],
            "top_k": parameters.get("top_k", 10),
        }
        collection = await chroma_client.get_or_create_collection(name="documents", embedding_function=ef)
        retrieved_docs = await retrieval_agent(
            query=query_params["query"],
            top_k=query_params["top_k"],
            chroma_collection=collection
        )
        # Refine response
        refined_text = await refinement_agent(
            openai_client=openai_client, context=str(retrieved_docs)
        )

        return refined_text

    except Exception as e:
        raise ValueError(f"Error during tool call handling: {str(e)}")


async def log_query(query_text: str, response_text: str, refined_text: str, duration: float):
    """
    Logs the query and response to the database.
    """
    log_entry = QueryLog(
        query=query_text,
        response=response_text,
        context=refined_text,
        duration=duration,
    )
    await log_entry.insert()


def get_tools_definition():
    return [
        {
            "type": "function",
            "function": {
                "name": "retrieve_documents",
                "description": "Retrieve relevant documents from the vector database based on a query.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search query."},
                        "top_k": {
                            "type": "integer",
                            "description": "Number of top documents to retrieve.",
                        },
                    },
                    "additionalProperties": False,
                    "required": ["query", "top_k"],
                },
            },
        }
    ]
