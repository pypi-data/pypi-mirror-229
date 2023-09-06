from bitbridge import AsyncBitBridgeFacade


async def test_async_get_best_block_hash(bridge_facade_config):
    facade_ = AsyncBitBridgeFacade(**bridge_facade_config)
    best_block_hash = await facade_.blockchain.get_best_block_hash()
    print(best_block_hash)


async def test_async_get_block(bridge_facade_config):
    facade_ = AsyncBitBridgeFacade(**bridge_facade_config)
    block = await facade_.blockchain.get_block(
        "0d36fae3b5a89547fa1fa29a678261c8a1690818927dbb996cf47d5b1737550a"
    )
    print(block)


async def test_async_get_blockchain_info(bridge_facade_config):
    facade_ = AsyncBitBridgeFacade(**bridge_facade_config)
    blockchain_info = await facade_.blockchain.get_blockchain_info()
    print(blockchain_info)
