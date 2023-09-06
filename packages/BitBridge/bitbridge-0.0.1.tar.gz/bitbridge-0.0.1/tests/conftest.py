import pytest


@pytest.fixture
def bridge_facade_config():
    return {
        "url": "http://localhost:18443",
        "username": "test_user",
        "password": "test_password",
    }
