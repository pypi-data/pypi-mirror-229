import pytest
from bitbridge.rpc.blockchain import BlockchainSync


@pytest.fixture
def blockchain_sync(rpc_delegate_sync):
    return BlockchainSync(rpc_delegate_sync)


@pytest.fixture
def blockhash_sync(blockchain_sync):
    best_block_hash_response = blockchain_sync.get_best_block_hash()
    return best_block_hash_response.get("result")


def test_get_best_block_hash(blockchain_sync):
    result = blockchain_sync.get_best_block_hash()
    assert result, "Expected a non-empty result"
    assert "result" in result, "Expected 'result' key in the response"


def test_get_block(blockchain_sync, blockhash_sync):
    result = blockchain_sync.get_block(blockhash_sync)
    assert result, "Expected a non-empty result"
    assert "result" in result, "Expected 'result' key in the response"


def test_get_blockchain_info(blockchain_sync):
    result = blockchain_sync.get_blockchain_info()
    assert result, "Expected a non-empty result"
    assert "result" in result, "Expected 'result' key in the response"
