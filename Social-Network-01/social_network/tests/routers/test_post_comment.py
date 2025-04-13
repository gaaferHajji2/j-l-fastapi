import pytest

from httpx import AsyncClient

async def create_post(body: str, async_client: AsyncClient, get_token: str):
    response = await async_client.post(
        url='/post/', 
        json={"body": body}, 
        headers={"Authorization": f"Bearer {get_token}"},
    )

    # For Debugging Only
    # print("The Status Code Is: ", response.status_code)
    # print("The Response Body Is: ", response.json())

    return response.status_code, response.json()

async def create_comment(body: str, post_id: int, async_client: AsyncClient, get_token: str):
    response = await async_client.post(
        url='/comment/', 
        json={"body": body, "post_id": post_id},
        headers={"Authorization": f"Bearer {get_token}"},
    )

    # For Debugging Only
    # print("The Status Code Is: ", response.status_code)
    # print("The Response Body Is: ", response.json())

    return response.status_code, response.json()


@pytest.fixture()
async def created_post(async_client: AsyncClient, get_token: str):
    return await create_post(
        "J-L-Test-01 Post", 
        async_client=async_client, 
        get_token=get_token
    )

@pytest.fixture()
async def created_comment(async_client: AsyncClient, get_token: str):
    return await create_comment(
        "J-L-Test-01 Comment", 
        1, 
        async_client=async_client, 
        get_token=get_token
    )

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

# Note Here: If We Don't Set created_post, Then The Test Will Fail
# Because db-fixture use autouse, so foreach test the db will be empty
# and no post will found
@pytest.mark.anyio
async def test_create_comment(created_post: tuple, created_comment: tuple):
    status_code, data = created_comment

    assert status_code == 201

    assert { "body": "J-L-Test-01 Comment", "post_id": 1}.items() <= data.items()