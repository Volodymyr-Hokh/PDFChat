from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from src.settings import settings

DATABASE_URL = settings.sqlalchemy_database_uri
engine = create_async_engine(DATABASE_URL)
Base = declarative_base()
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session() as db:
        yield db
