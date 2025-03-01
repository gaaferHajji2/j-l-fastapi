from typing import AsyncGenerator, Generator

import pytest

from fastapi.testclient import TestClient

from httpx import AsyncClient

from main import app

from routes.post import post_table

from routes.comment import comment_table

@pytest.fixture()
def client()-> Generator:
    yield TestClient(app=app)