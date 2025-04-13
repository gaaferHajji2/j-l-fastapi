import pytest

from httpx import AsyncClient

from social_network.security import (
    get_user_by_email,
    verify_password,
    get_password_hash,
    create_access_token,
)

# print("The Name Is: ", __name__)


@pytest.mark.anyio
async def test_get_user(registered_user: dict):
    result = await get_user_by_email(registered_user["email"])

    assert result is not None

    assert result.email == registered_user["email"]


def test_password_hashing():
    password = "password"

    assert verify_password(password, get_password_hash(password))


@pytest.mark.anyio
async def test_create_expired_token(
    async_client: AsyncClient, registered_user: dict, mocker
):
    mocker.patch("social_network.security.get_token_expire_minutes", return_value=-1)

    token = create_access_token(email=registered_user["email"])

    response = await async_client.post(
        "/post/",
        json={
            "body": "Test Body",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    print("The Json Response For Expired Token Is: ", response.json())

    assert response.status_code not in (200, 201)

    assert response.status_code == 401
