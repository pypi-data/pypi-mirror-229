from bitbridge.rpc.base_rpc import BaseRPC
from bitbridge.utils.constants import (
    CREATE_MULTI_SIG,
    ESTIMATE_SMART_FEE,
    VALIDATE_ADDRESS,
)


class BaseUtil(BaseRPC):
    pass


class UtilSync(BaseUtil):
    def create_multi_sig(self, nrequired: int, keys: list, address_type: str = None):
        return self.rpc_delegate.send_request(
            CREATE_MULTI_SIG, [nrequired, keys, address_type]
        )

    def estimate_smart_fee(self, conf_target: int, estimate_mode: str = None):
        return self.rpc_delegate.send_request(
            ESTIMATE_SMART_FEE, [conf_target, estimate_mode]
        )

    def validate_address(self, address: str):
        return self.rpc_delegate.send_request(VALIDATE_ADDRESS, [address])


class UtilAsync(BaseUtil):
    async def create_multi_sig(
        self, nrequired: int, keys: list, address_type: str = None
    ):
        return await self.rpc_delegate.send_request_async(
            CREATE_MULTI_SIG, [nrequired, keys, address_type]
        )

    async def estimate_smart_fee(self, conf_target: int, estimate_mode: str = None):
        return await self.rpc_delegate.send_request_async(
            ESTIMATE_SMART_FEE, [conf_target, estimate_mode]
        )

    async def validate_address(self, address: str):
        return await self.rpc_delegate.send_request_async(VALIDATE_ADDRESS, [address])
