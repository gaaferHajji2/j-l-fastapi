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
async def test_create_post(created_post: tuple):
    assert created_post[0] == 201
    assert {"body": "J-L-Test-01 Post"}.items() <= created_post[1].items()

@pytest.mark.anyio
async def test_create_post_without_body(async_client: AsyncClient):
    response = await async_client.post("/post/", json={})

    assert response.status_code == 422

@pytest.mark.anyio
async def test_get_all_posts(async_client: AsyncClient, created_post: tuple):
    _, __ = created_post
    response = await async_client.get('/post/')

    data = response.json()

    assert response.status_code == 200

    assert len(data) > 0

    assert type(data[0]) is dict
    