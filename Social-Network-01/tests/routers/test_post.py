import pytest

from httpx import AsyncClient

async def create_post(body: str, async_client: AsyncClient):
    response = await async_client.post(url='/post', json={"body": body})

    return response.json()

@pytest.fixture()
async def created_post(async_client: AsyncClient):
    return await create_post("J-L-Test-01 Post", async_client=async_client)