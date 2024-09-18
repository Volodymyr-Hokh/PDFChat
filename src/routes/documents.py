import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.chat.process_pdf import create_embeddings_for_pdf
from src.database.db import get_db
from src.database.repository.documents import (
    save_document,
    get_users_documents,
    delete_document,
)
from src.schemas import Document as DocumentSchema
from src.services.auth import auth_service


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    if file.content_type != "application/pdf":
        print(file.content_type)
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    save_directory = Path("storage")
    save_directory.mkdir(exist_ok=True)
    file_name = f"{uuid4()}.pdf"

    file_path = save_directory / file_name

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document = DocumentSchema(
        name=file.filename,
        file_path=file_path.as_posix(),
        user_id=user.id,
    )
    document_db = await save_document(db, document)

    # TODO Rewrite this to use a task queue
    await create_embeddings_for_pdf(document_id=document_db.id, document_path=file_path)
    return document_db


@router.get("/")
async def get_documents(
    db: AsyncSession = Depends(get_db), user=Depends(auth_service.get_current_user)
):
    return await get_users_documents(db, user.id)


@router.delete("/{document_id}")
async def delete_document_by_id(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    documents = await get_users_documents(db, user.id)
    if document_id not in [document.id for document in documents]:
        raise HTTPException(status_code=404, detail="Document not found.")
    await delete_document(db, document_id)
    return {"message": "Document deleted successfully."}
