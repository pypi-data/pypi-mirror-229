from utils.constants import GET_BEST_BLOCK_HASH, GET_BLOCK, GET_BLOCKCHAIN_INFO


class BlockchainAsync:
    def __init__(self, base_rpc):
        self._rpc = base_rpc

    async def get_best_block_hash(self):
        return await self._rpc.send_request_async(GET_BEST_BLOCK_HASH)

    async def get_block(self, blockhash: str, verbosity: int = 1):
        return await self._rpc.send_request_async(GET_BLOCK, [blockhash, verbosity])

    async def get_blockchain_info(self):
        return await self._rpc.send_request_async(GET_BLOCKCHAIN_INFO)
