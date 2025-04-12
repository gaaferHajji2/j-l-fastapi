import pytest

from social_network.security import get_user_by_email, verify_password, get_password_hash

# print("The Name Is: ", __name__)

@pytest.mark.anyio
async def test_get_user(registered_user: dict):
    result = await get_user_by_email(registered_user["email"])

    assert result is not None

    assert result.email == registered_user["email"]

def test_password_hashing():
    password = "password"

    assert verify_password(password, get_password_hash(password))