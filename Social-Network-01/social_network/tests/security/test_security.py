import pytest

from social_network.security import get_user_by_email

@pytest.mark.anyio
async def test_get_user(registered_user: dict):
    result = await get_user_by_email(registered_user["email"])

    assert result is not None

    assert result.email == registered_user["email"]