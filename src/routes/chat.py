from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.chat.chains import build_rag_chain
from src.database.db import get_db
from src.database.repository.chat import (
    create_chat,
    get_chat_by_id,
    save_message,
    get_chats_by_document_id,
    load_chat_history,
    rename_chat,
    delete_chat,
    get_user_chats,
)
from src.database.repository.documents import get_users_documents
from src.enums import Role
from src.schemas import Chat as ChatSchema, Message as MessageSchema
from src.services.auth import auth_service


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message")
async def save_message_endpoint(
    message: MessageSchema,
    db: AsyncSession = Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    chats = await get_user_chats(db, user.id)
    if message.chat_id not in [chat.id for chat in chats]:
        raise HTTPException(status_code=404, detail="Chat not found")

    message.role = Role.HUMAN
    await save_message(db, message)
    chat = await get_chat_by_id(db, message.chat_id)
    chain, chat_history = await build_rag_chain(chat.document_id, chat.id, db)
    input_data = {"input": message.content, "chat_history": chat_history}

    response = await chain.ainvoke(input_data)
    response_message = MessageSchema(
        chat_id=message.chat_id,
        content=response,
        role=Role.AI,
    )
    await save_message(db, response_message)
    return response


@router.post("/")
async def create_chat_endpoint(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(auth_service.get_current_user),
    name: Optional[str] = None,
):
    return await create_chat(
        db, ChatSchema(document_id=document_id, user_id=user.id, name=name)
    )


@router.get("/{chat_id}")
async def get_chat_by_id_endpoint(
    chat_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    chats = await get_user_chats(db, user.id)
    if chat_id not in [chat.id for chat in chats]:
        raise HTTPException(status_code=404, detail="Chat not found")
    return await get_chat_by_id(db, chat_id)


@router.get("/document/{document_id}")
async def get_chats_by_document_id_endpoint(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    documents = await get_users_documents(db, user.id)
    if document_id not in [document.id for document in documents]:
        raise HTTPException(status_code=404, detail="Document not found")
    return await get_chats_by_document_id(db, document_id)


@router.get("/history/{chat_id}")
async def get_chat_history(
    chat_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    chats = await get_user_chats(db, user.id)
    if chat_id not in [chat.id for chat in chats]:
        raise HTTPException(status_code=404, detail="Chat not found")
    chat = await get_chat_by_id(db, chat_id)
    history = await load_chat_history(db, chat.id)
    return history


@router.put("/{chat_id}")
async def rename_chat_endpoint(
    chat_id: int,
    name: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    chats = await get_user_chats(db, user.id)
    if chat_id not in [chat.id for chat in chats]:
        raise HTTPException(status_code=404, detail="Chat not found")
    return await rename_chat(db, chat_id, name)


@router.delete("/{chat_id}")
async def delete_chat_endpoint(
    chat_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    chats = await get_user_chats(db, user.id)
    if chat_id not in [chat.id for chat in chats]:
        raise HTTPException(status_code=404, detail="Chat not found")
    return await delete_chat(db, chat_id)
