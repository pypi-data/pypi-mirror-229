from bitbridge.rpc.base_rpc import BaseRPC
from bitbridge.utils.constants import (
    DECODE_RAW_TRANSACTION,
    DECODE_SCRIPT,
    GET_RAW_TRANSACTION,
    SEND_RAW_TRANSACTION,
    CREATE_RAW_TRANSACTION,
    SIGNRAW_TRANSACTION_WITH_WALLET,
)


class BaseRawTransaction(BaseRPC):
    pass


class RawTransactionSync(BaseRawTransaction):
    def decode_raw_transaction(self, hexstring: str):
        return self.rpc_delegate.send_request(DECODE_RAW_TRANSACTION, [hexstring])

    def decode_script(self, hexstring: str):
        return self.rpc_delegate.send_request(DECODE_SCRIPT, [hexstring])

    def get_raw_transaction(self, txid: str, verbose: bool = False):
        return self.rpc_delegate.send_request(GET_RAW_TRANSACTION, [txid, verbose])

    def send_raw_transaction(self, hexstring: str, maxfeerate: float = 0.10):
        return self.rpc_delegate.send_request(
            SEND_RAW_TRANSACTION, [hexstring, maxfeerate]
        )

    def create_raw_transaction(self, inputs: list, outputs: dict):
        return self.rpc_delegate.send_request(CREATE_RAW_TRANSACTION, [inputs, outputs])

    def signraw_transaction_with_wallet(self, hexstring: str):
        return self.rpc_delegate.send_request(
            SIGNRAW_TRANSACTION_WITH_WALLET, [hexstring]
        )


class RawTransactionAsync(BaseRawTransaction):
    async def decode_raw_transaction(self, hexstring: str):
        return await self.rpc_delegate.send_request_async(
            DECODE_RAW_TRANSACTION, [hexstring]
        )

    async def decode_script(self, hexstring: str):
        return await self.rpc_delegate.send_request_async(DECODE_SCRIPT, [hexstring])

    async def get_raw_transaction(self, txid: str, verbose: bool = False):
        return await self.rpc_delegate.send_request_async(
            GET_RAW_TRANSACTION, [txid, verbose]
        )

    async def send_raw_transaction(self, hexstring: str, maxfeerate: float = 0.10):
        return await self.rpc_delegate.send_request_async(
            SEND_RAW_TRANSACTION, [hexstring, maxfeerate]
        )

    async def create_raw_transaction(self, inputs: list, outputs: dict):
        return await self.rpc_delegate.send_request_async(
            CREATE_RAW_TRANSACTION, [inputs, outputs]
        )

    async def signraw_transaction_with_wallet(self, hexstring: str):
        return await self.rpc_delegate.send_request_async(
            SIGNRAW_TRANSACTION_WITH_WALLET, [hexstring]
        )
