import pathlib

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Document
from src.schemas import Document as DocumentSchema
from src.chat.vector_store import delete_document_async as delete_document_vector_store


async def save_document(db: AsyncSession, document: DocumentSchema) -> Document:
    new_document = Document(**document.model_dump())
    db.add(new_document)
    await db.commit()
    return new_document


async def get_users_documents(db: AsyncSession, user_id: int) -> list[Document]:
    stmt = select(Document).where(Document.user_id == user_id)
    result = await db.execute(stmt)
    documents = result.scalars().all()
    return documents


async def delete_document(db: AsyncSession, document_id: int):
    stmt = select(Document).where(Document.id == document_id)
    result = await db.execute(stmt)
    document = result.scalars().first()
    if not document:
        return
    document_path = pathlib.Path(document.file_path)
    if document_path.exists():
        document_path.unlink()
    await db.delete(document)
    await db.commit()
    await delete_document_vector_store(document_id)
