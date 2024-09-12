from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from src.settings import settings

async_engine = create_async_engine(settings.db.url(), future=True, echo=False)
AsyncSessionLocal = sessionmaker(
    async_engine, expire_on_commit=False, autocommit=False, autoflush=False, class_=AsyncSession
)

Base = declarative_base()


async def get_db() -> Generator:
    try:
        session: AsyncSession = AsyncSessionLocal()
        yield session
    finally:
        await session.close()
