import time

from chromadb import AsyncClientAPI, EmbeddingFunction
from fastapi import Depends, HTTPException, APIRouter
from openai import AsyncOpenAI

from CommunereRAG.services.chroma.dependency import get_chroma_client, get_ef
from CommunereRAG.services.openai.dependency import get_openai_client
from CommunereRAG.web.api.query.agent_utils import (
    run_agent_chain,
    log_query,
    get_tools_definition,
)
from CommunereRAG.web.api.query.schema import QueryRequest

router = APIRouter()


@router.post("")
async def query_document(
    payload: QueryRequest,
    openai_client: AsyncOpenAI = Depends(get_openai_client),
    chroma_client: AsyncClientAPI = Depends(get_chroma_client),
    ef: EmbeddingFunction = Depends(get_ef),
):
    """
    Query endpoint where GPT-4o dynamically retrieves information via tool calling.
    """
    start_time = time.time()
    query_text = payload.query

    try:
        # Define tool schema for document retrieval
        tools = get_tools_definition()

        # Call GPT-4o with tool schema
        system_prompt = {
            "role": "system",
            "content": "Your task is to answer user's questions based on the tool_call result. You can only use one tool_call.",
        }
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

        tool_call = response_text.tool_calls[0].function
        tool_call_id = response_text.tool_calls[0].id

        refined_text = await run_agent_chain(
            tool_call, openai_client, chroma_client, ef
        )

        # Generate the final response
        final_response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                system_prompt,
                {"role": "user", "content": query_text},
                response_text,
                {
                    "role": "tool",
                    "content": refined_text,
                    "tool_call_id": tool_call_id,
                },
            ],
        )
        response_text = final_response.choices[0].message.content

        # Log the query and response
        await log_query(
            query_text, response_text, refined_text, time.time() - start_time
        )

        return {"response": response_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
