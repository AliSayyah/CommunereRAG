import base64
import traceback

from fastapi import APIRouter, UploadFile, HTTPException, Body
from fastapi.param_functions import Depends
from fastapi.params import File
from loguru import logger

from CommunereRAG.web.api.upload.schema import DocumentMetadata
from CommunereRAG.web.api.upload.tasks import process_document_task

router = APIRouter()


@router.post("")
async def upload_document(
    file: UploadFile,
    metadata: DocumentMetadata = Depends(),
):
    try:
        # Save file content to memory
        file_content = file.file.read()
        if not file_content.strip():
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        # Encode bytes as Base64 string
        file_content_base64 = base64.b64encode(file_content).decode("utf-8")
        # Send the task to the background worker
        await process_document_task.kiq(file_content_base64, metadata.model_dump())

        return {"message": "Document is being processed"}

    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
