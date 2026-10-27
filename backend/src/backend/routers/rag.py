import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from ..dependencies import get_current_user
from ..models import User
from ..rag_store import extract_and_store_pdf, delete_session_documents

router = APIRouter(tags=["rag"])


@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    session_id: str = Form(None),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        # Generate session if it doesn't exist yet
        active_session_id = session_id or str(uuid.uuid4())
        file_bytes = await file.read()

        extract_and_store_pdf(file_bytes, active_session_id)

        return {
            "status": "success",
            "session_id": active_session_id,
            "filename": file.filename,
            "message": "PDF uploaded and indexed successfully.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session-docs/{session_id}")
def delete_pdf(session_id: str, current_user: User = Depends(get_current_user)):
    delete_session_documents(session_id)
    return {"status": "success", "message": "PDF data cleared for session."}
