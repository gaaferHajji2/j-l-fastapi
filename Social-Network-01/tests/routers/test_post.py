import pytest

from httpx import AsyncClient

async def create_post(body: str, async_client: AsyncClient):
    response = await async_client.post(url='/post/', json={"body": body})

    # For Debugging Only
    # print("The Status Code Is: ", response.status_code)
    # print("The Response Body Is: ", response.json())

    return response.status_code, response.json()

@pytest.fixture()
async def created_post(async_client: AsyncClient):
    return await create_post("J-L-Test-01 Post", async_client=async_client)

@pytest.mark.anyio
async def test_create_post(created_post):
    assert created_post[0] == 201
    assert {"body": "J-L-Test-01 Post"}.items() <= created_post[1].items()

@pytest.mark.anyio
async def test_create_post_without_body(async_client: AsyncClient):
    response = await async_client.post("/post/", json={})

    assert response.status_code == 422