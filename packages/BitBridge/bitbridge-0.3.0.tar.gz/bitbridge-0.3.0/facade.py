from bitbridge.rpc.base import BitBridgeBaseRPC
from rpc._sync.blockchain import BlockchainSync


class BitBridgeFacade:
    def __init__(self, url: str, username: str, password: str):
        base_rpc = BitBridgeBaseRPC(url, username, password)
        self.blockchain = BlockchainSync(base_rpc)
