import os

from typing import AsyncGenerator, Generator

import pytest

from fastapi.testclient import TestClient

from httpx import ASGITransport, AsyncClient

import logging

os.environ["ENV_STATE"] = "test"

from social_network.main import app

# from routes.post import post_table

# from routes.comment import comment_table

from social_network.database import database

logger = logging.getLogger(__name__)

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

@pytest.fixture()
async def registered_user(async_client: AsyncClient) -> dict:
    user_details = {"email": "jafar@loka.com", "password": "Test@123"}

    response = await async_client.post('/user/register', json=user_details)

    # print(f"The Response Data Is: {response.content}")
    # print(f"The Response Status Code Is: {response.status_code}")

    result = response.json()

    # logger.debug(f"The Response Status Code: {response.status_code}")
    # logger.debug(f"The Response Body Is: {user_details}")
    # logger.debug(f"The ID Of User Is: {result["id"]}", )

    user_details["id"] = result["id"]

    return user_details

@pytest.fixture()
async def get_token(async_client: AsyncClient, registered_user: dict) -> str:
    response  = await async_client.post(url='/token', json=registered_user)

    return response.json()["access_token"]