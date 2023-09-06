from bitbridge.rpc.base import BitBridgeBaseRPC
from rpc._async.blockchain import BlockchainAsync


class AsyncBitBridgeFacade:
    def __init__(self, url: str, username: str, password: str):
        base_rpc = BitBridgeBaseRPC(url, username, password)
        self.blockchain = BlockchainAsync(base_rpc)
