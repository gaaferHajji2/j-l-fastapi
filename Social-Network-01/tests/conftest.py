import os

from typing import AsyncGenerator, Generator

import pytest

from fastapi.testclient import TestClient

from httpx import ASGITransport, AsyncClient

os.environ["ENV_STATE"] = "test"

from main import app

from routes.post import post_table

from routes.comment import comment_table

from database import database

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture()
def client() -> Generator:
    yield TestClient(app=app)

@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    # comment_table.clear()
    # post_table.clear()

    await database.connect()

    yield

    await database.disconnect()

@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(transport=ASGITransport(app=app),base_url=client.base_url) as ac:
        yield ac