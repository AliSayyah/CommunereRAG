import time

from chromadb import AsyncClientAPI, EmbeddingFunction
from fastapi import Depends, HTTPException, APIRouter
from openai import AsyncOpenAI

from CommunereRAG.db.models.query_model import QueryLog
from CommunereRAG.services.chroma.dependency import get_chroma_client, get_ef
from CommunereRAG.services.openai.dependency import get_openai_client
from CommunereRAG.web.api.query.agents import retrieval_agent, refinement_agent
from CommunereRAG.web.api.query.schema import QueryRequest

router = APIRouter()

@router.post("")
async def query_document(
    payload: QueryRequest,
    openai_client: AsyncOpenAI=Depends(get_openai_client),
    chroma_client: AsyncClientAPI=Depends(get_chroma_client),
    ef: EmbeddingFunction = Depends(get_ef),
):
    """
    Query endpoint where GPT-4o dynamically retrieves information via function calling.
    """
    start_time = time.time()
    try:
        query_text = payload.query

        # Define retrieval function schema
        tools = [
            {
                "type": "function",
                "function": {
                "name": "retrieve_documents",
                "description": "Retrieve relevant documents from the database based on a query.",
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
            }
            }
        ]
        system_prompt = {
            "role": "system",
            "content": "Your task is to answer user's questions based on the tool_call result. you can only use one tool_call.",
        }
        # Call GPT-4 with the retrieval function schema
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                system_prompt,
                {"role": "user", "content": query_text},
            ],
            tools=tools,
            tool_choice="required",
        )
        response_text = response.choices[0].message
        # Process function call request
        if response_text.tool_calls:
            tool_call = response_text.tool_calls[0].function
            tool_call_id = response_text.tool_calls[0].id
            if tool_call.name == "retrieve_documents":
                # Extract parameters from the function call
                parameters = tool_call.arguments
                query_params = eval(parameters)  # Convert JSON string to dictionary
                collection = await chroma_client.get_or_create_collection(name="documents", embedding_function=ef)
                retrieved_docs = await retrieval_agent(
                    query=query_params["query"],
                    top_k=query_params.get("top_k", 5),
                    chroma_collection=collection
                )

                # Pass retrieved context back to refinement_agent
                refined_text = await refinement_agent(openai_client=openai_client, query=query_text, context=str(retrieved_docs))
                final_response = await openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        system_prompt,
                        {"role": "user", "content": query_text},
                        response_text,
                        {
                            "role": "tool",
                            "content": refined_text,
                            "tool_call_id": tool_call_id
                        },
                    ],
                )
                response_text = final_response.choices[0].message.content
                duration = time.time() - start_time
                log_entry = QueryLog(
                    query=query_text,
                    response=response_text,
                    context=refined_text,
                    duration=duration,
                )
                await log_entry.insert()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"response":response_text}


