import pytest
from os import getenv

from faker import Faker

from bitbridge.rpc.config import BitBridgeConfig
from bitbridge.rpc_delegate import RpcDelegate
from bitbridge.utils.enums import Mode


@pytest.fixture(scope="session")
def fake():
    return Faker()


@pytest.fixture
def bridge_facade_config():
    user = getenv("RPC_USER", "user")
    password = getenv("RPC_PASS", "password")
    return {
        "url": "http://localhost:18443",
        "username": user,
        "password": password,
    }


@pytest.fixture
def bridge_config(bridge_facade_config):
    return BitBridgeConfig(**bridge_facade_config)


# Create a fixture for RpcDelegate
@pytest.fixture
def rpc_delegate_sync(bridge_config):
    return RpcDelegate(bridge_config, mode=Mode.SYNC)


@pytest.fixture
def rpc_delegate_async(bridge_config):
    return RpcDelegate(bridge_config, mode=Mode.ASYNC)
