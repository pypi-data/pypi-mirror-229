import pytest

from bitbridge.rpc.blockchain import BlockchainAsync


@pytest.fixture
def blockchain_async(rpc_delegate_async):
    return BlockchainAsync(rpc_delegate_async)


@pytest.fixture
async def blockhash_async(blockchain_async):
    best_block_hash_response = await blockchain_async.get_best_block_hash()
    return best_block_hash_response.get("result")


async def test_async_get_best_block_hash(blockchain_async):
    result = await blockchain_async.get_best_block_hash()
    assert result, "Expected a non-empty result"
    assert "result" in result, "Expected 'result' key in the response"


async def test_async_get_block(blockchain_async, blockhash_async):
    result = await blockchain_async.get_block(blockhash_async)
    assert result, "Expected a non-empty result"
    assert "result" in result, "Expected 'result' key in the response"


async def test_async_get_blockchain_info(blockchain_async):
    result = await blockchain_async.get_blockchain_info()
    assert result, "Expected a non-empty result"
    assert "result" in result, "Expected 'result' key in the response"
