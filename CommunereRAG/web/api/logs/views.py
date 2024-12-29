from typing import List

from fastapi import APIRouter, HTTPException

from CommunereRAG.db.models.query_model import QueryLog

router = APIRouter()


@router.get("")
async def get_logs(limit: int = 10):
    """
    Fetch the most recent query logs.
    """
    try:
        logs = await QueryLog.find_all().sort("-timestamp").limit(limit).to_list()
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not retrieve logs.")
