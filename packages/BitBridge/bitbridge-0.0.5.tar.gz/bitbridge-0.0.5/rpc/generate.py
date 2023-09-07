from bitbridge.rpc.base_rpc import BaseRPC
from bitbridge.utils.constants import (
    GENERATE_BLOCK,
    GENERATE_TO_ADDRESS,
    GENERATE_TO_DESCRIPTOR,
)


class BaseGenerate(BaseRPC):
    pass


class GenerateSync(BaseGenerate):
    def generate_block(self, num_blocks: int):
        return self.rpc_delegate.send_request(GENERATE_BLOCK, [num_blocks])

    def generate_to_address(
        self, num_blocks: int, address: str, maxtries: int = 1000000
    ):
        return self.rpc_delegate.send_request(
            GENERATE_TO_ADDRESS, [num_blocks, address, maxtries]
        )

    def generate_to_descriptor(
        self, num_blocks: int, descriptor: str, maxtries: int = 1000000
    ):
        return self.rpc_delegate.send_request(
            GENERATE_TO_DESCRIPTOR, [num_blocks, descriptor, maxtries]
        )


class GenerateAsync(BaseGenerate):
    async def generate_block(self, num_blocks: int):
        return await self.rpc_delegate.send_request_async(GENERATE_BLOCK, [num_blocks])

    async def generate_to_address(
        self, num_blocks: int, address: str, maxtries: int = 1000000
    ):
        return await self.rpc_delegate.send_request_async(
            GENERATE_TO_ADDRESS, [num_blocks, address, maxtries]
        )

    async def generate_to_descriptor(
        self, num_blocks: int, descriptor: str, maxtries: int = 1000000
    ):
        return await self.rpc_delegate.send_request_async(
            GENERATE_TO_DESCRIPTOR, [num_blocks, descriptor, maxtries]
        )
