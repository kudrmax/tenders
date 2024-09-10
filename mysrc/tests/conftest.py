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


@pytest.fixture(scope='function', autouse=True)
async def setup_test_db():
    if os.path.exists(DB_TEST_PATH):
        os.remove(DB_TEST_PATH)
    sync_engine = create_engine(DB_TEST_URL_SYNC, echo=False)
    Base.metadata.create_all(bind=sync_engine)


async def get_db_test() -> Generator:
    engine = create_async_engine(DB_TEST_URL, future=True, echo=False)
    AsyncSessionLocalTest = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    try:
        session_test: AsyncSession = AsyncSessionLocalTest()
        yield session_test
    finally:
        await session_test.close()
        if os.path.exists(DB_TEST_PATH):
            os.remove(DB_TEST_PATH)


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


@pytest.fixture(scope="function")
async def async_session() -> AsyncSession:
    engine = create_async_engine(DB_TEST_URL, future=True, echo=False)
    AsyncSessionLocalTest = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with AsyncSessionLocalTest() as session:
        yield session
