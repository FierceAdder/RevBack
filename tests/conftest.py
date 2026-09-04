"""Pytest test configuration and fixtures."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from src.models.db_models import Base


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncSession:
    """Provides an isolated in-memory SQLite database session for each test."""
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSession = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with TestSession() as session:
        yield session

    await test_engine.dispose()
