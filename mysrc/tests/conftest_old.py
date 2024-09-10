import asyncio
import os
from typing import Any
from typing import Generator

import asyncpg
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text, create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from starlette.testclient import TestClient

from mysrc.database import get_db, Base
from mysrc.api.tenders.models import MTender
from mysrc.api.organisations.models import MOrganization, MOrganizationResponsible
from mysrc.api.employees.models import MEmployee
# from mysrc.api.binds.models import MTender
from mysrc.main import app
from mysrc.settings import DB_TEST_URL, DB_TEST_URL_SYNC, DB_TEST_PATH


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session', autouse=True)
async def setup_test_db():
    async_engine = create_async_engine(DB_TEST_URL, future=True, echo=False)
    sync_engine = create_engine(DB_TEST_URL_SYNC, echo=True)
    AsyncSessionLocal = sessionmaker(
        async_engine, expire_on_commit=False, autocommit=False, autoflush=False, class_=AsyncSession
    )

    Base.metadata.create_all(bind=sync_engine)


async def get_db_test(setup_test_db) -> Generator:
    engine = create_async_engine(DB_TEST_URL, future=True, echo=False)
    AsyncSessionLocalTest = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    try:
        session_test: AsyncSession = AsyncSessionLocalTest()
        yield session_test
    finally:
        await session_test.close()
        if os.path.exists(DB_TEST_PATH):
            os.remove(DB_TEST_PATH)


#
# @pytest.fixture(scope="function", autouse=True)
# async def clean_tables():
#     engine = create_async_engine(settings.db_test.url, future=True, echo=False)
#     AsyncSessionLocalTest = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
#     session_test: AsyncSession = AsyncSessionLocalTest()
#     async with session_test.begin():
#         for table_for_cleaning in CLEAN_TABLES:
#             await session_test.execute(text(f"""TRUNCATE TABLE {table_for_cleaning};"""))


@pytest.fixture(scope="session")
async def asyncpg_pool():
    pool = await asyncpg.create_pool(
        "".join(DB_TEST_URL_SYNC)
    )
    yield pool
    pool.close()


@pytest.fixture(scope="function")
async def client() -> Generator[TestClient, Any, None]:
    app.dependency_overrides[get_db] = get_db_test
    with TestClient(app) as client:
        yield client


# @pytest.fixture
# async def create_contact_in_database(asyncpg_pool):
#     async def create_contact_in_database(name: str):
#         async with asyncpg_pool.acquire() as connection:
#             return await connection.execute(
#                 """INSERT INTO contacts (name) VALUES ($1)""", name
#             )
#
#     return create_contact_in_database


@pytest.fixture(scope="function")
async def async_session() -> AsyncSession:
    engine = create_async_engine(DB_TEST_URL, future=True, echo=False)
    AsyncSessionLocalTest = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with AsyncSessionLocalTest() as session:
        yield session
        # await session.rollback()


# @pytest.fixture(scope="function", autouse=True)
# async def clear_db(async_session: AsyncSession):
#     async with async_session.begin():
#         for table in Base.metadata.sorted_tables:
#             await async_session.execute(text(f"DELETE FROM {table.name}"))
#         await async_session.commit()