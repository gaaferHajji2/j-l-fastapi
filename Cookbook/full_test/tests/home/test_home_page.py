from httpx import AsyncClient
import pytest

@pytest.mark.asyncio
async def test_get_home(async_client: AsyncClient):
    # print(type(async_client))
    response = await async_client.get(url='/home')
    assert response.status_code == 200
    assert response.json() is not None