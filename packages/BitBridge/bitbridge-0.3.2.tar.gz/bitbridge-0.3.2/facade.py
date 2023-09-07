from bitbridge.rpc.blockchain import BlockchainSync, BlockchainAsync
from bitbridge.rpc.wallet import WalletSync, WalletAsync
from bitbridge.rpc.raw_transaction import RawTransactionSync, RawTransactionAsync
from bitbridge.rpc.generate import GenerateSync, GenerateAsync
from bitbridge.rpc.util import UtilSync, UtilAsync
from bitbridge.rpc.config import BitBridgeConfig
from bitbridge.rpc_delegate import RpcDelegate
from bitbridge.utils.enums import Mode


class BaseBitBridgeFacade:
    rpc_delegate: RpcDelegate

    def __init__(self, config: BitBridgeConfig):
        self.config = config


class BitBridgeFacade(BaseBitBridgeFacade):
    def __init__(self, config: BitBridgeConfig):
        super().__init__(config)
        self.rpc_delegate = RpcDelegate(config, mode=Mode.SYNC)
        self.blockchain = BlockchainSync(self.rpc_delegate)
        self.wallet = WalletSync(self.rpc_delegate)
        self.raw_transaction = RawTransactionSync(self.rpc_delegate)
        self.generate = GenerateSync(self.rpc_delegate)
        self.util = UtilSync(self.rpc_delegate)


class AsyncBitBridgeFacade(BaseBitBridgeFacade):
    def __init__(self, config: BitBridgeConfig):
        super().__init__(config)
        self.rpc_delegate = RpcDelegate(config, mode=Mode.ASYNC)
        self.blockchain = BlockchainAsync(self.rpc_delegate)
        self.wallet = WalletAsync(self.rpc_delegate)
        self.raw_transaction = RawTransactionAsync(self.rpc_delegate)
        self.generate = GenerateAsync(self.rpc_delegate)
        self.util = UtilAsync(self.rpc_delegate)
