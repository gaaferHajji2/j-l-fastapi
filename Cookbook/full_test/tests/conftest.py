from typing import AsyncGenerator
import pytest, pytest_asyncio
from httpx import ASGITransport, AsyncClient
from fastapi.testclient import TestClient
from full_test.src.app import app

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest_asyncio.fixture()
async def client() -> AsyncGenerator:
    yield TestClient(app=app)

@pytest_asyncio.fixture()
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(transport=ASGITransport(app=app), base_url=client.base_url) as ac:
        yield ac
