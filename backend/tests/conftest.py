"""
Pytest configuration and shared fixtures.

Uses an in-memory SQLite database (via aiosqlite) so tests run without
a real PostgreSQL instance.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def engine():
    """Create a fresh in-memory SQLite engine per test function."""
    _engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(engine):
    """Provide a DB session per test."""
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """
    Async HTTP test client with DB dependency overridden to use test session.
    """
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


def make_opportunity_data(**overrides) -> dict:
    """Return a minimal valid opportunity payload."""
    base = {
        "title": "Test Scholarship 2025",
        "organization": "Test University",
        "description": "A test scholarship for unit testing.",
        "category": "scholarship",
        "tags": ["Student", "Scholarship"],
        "country": ["India", "Global"],
        "is_remote": True,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": True,
        "age_limit": "Under 30",
        "eligibility": "Open to all students.",
        "funding_amount": "Fully funded",
        "application_fee": "Free",
        "link": "https://example.com/test-scholarship",
        "source_name": "Test Source",
        "deadline": "2025-12-31",
        "is_expired": False,
    }
    base.update(overrides)
    return base
