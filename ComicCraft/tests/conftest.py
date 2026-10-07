import os


# Use mock mode for automated tests.
os.environ["AI_MODE"] = "mock"


import pytest

from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app


@pytest.fixture()
def client():

    get_settings.cache_clear()

    return TestClient(app)