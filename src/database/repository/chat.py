from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain.schema import HumanMessage, AIMessage

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Message, Chat
from src.schemas import Message as MessageSchema, Chat as ChatSchema
from src.enums import Role


async def get_chat_by_id(db: AsyncSession, chat_id: int) -> Chat:
    stmt = select(Chat).where(Chat.id == chat_id)
    result = await db.execute(stmt)
    chat = result.scalars().first()
    return chat


async def create_chat(db: AsyncSession, chat: ChatSchema) -> Chat:
    new_chat = Chat(**chat.model_dump())
    db.add(new_chat)
    await db.commit()
    return new_chat


async def save_message(db: AsyncSession, message: MessageSchema) -> Message:
    chat = await get_chat_by_id(db, message.chat_id)
    if not chat:
        raise ValueError(f"Chat with id {message.chat_id} not found")
    new_message = Message(**message.model_dump())
    db.add(new_message)
    await db.commit()
    return new_message


async def load_chat_history(db: AsyncSession, chat_id: int) -> BaseChatMessageHistory:
    chat_history = ChatMessageHistory()
    result = await db.execute(select(Message).where(Message.chat_id == chat_id))
    messages = result.scalars().all()
    for message in messages:
        if message.role == Role.HUMAN:
            chat_history.add_message(HumanMessage(content=message.content))
        elif message.role == Role.AI:
            chat_history.add_message(AIMessage(content=message.content))
    return chat_history


async def get_chats_by_document_id(db: AsyncSession, document_id: int) -> list[Chat]:
    stmt = select(Chat).where(Chat.document_id == document_id)
    result = await db.execute(stmt)
    chats = result.scalars().all()
    return chats


async def rename_chat(db: AsyncSession, chat_id: int, name: str) -> Chat:
    chat = await get_chat_by_id(db, chat_id)
    chat.name = name
    await db.commit()
    return chat


async def delete_chat(db: AsyncSession, chat_id: int) -> None:
    chat = await get_chat_by_id(db, chat_id)
    await db.delete(chat)
    await db.commit()


async def get_user_chats(db: AsyncSession, user_id: int) -> list[Chat]:
    stmt = select(Chat).where(Chat.user_id == user_id)
    result = await db.execute(stmt)
    chats = result.scalars().all()
    return chats
