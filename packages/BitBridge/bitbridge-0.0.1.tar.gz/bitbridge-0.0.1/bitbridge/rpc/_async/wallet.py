from utils.constants import ABANDON_TRANSACTION, ABORT_RESCAN, ADD_MULTISIG_ADDRESS


class WalletAsync:
    def __init__(self, base_rpc):
        self._rpc = base_rpc

    async def abandon_transaction(self, txid: str):
        """
        Mark in-wallet transaction <txid> as abandoned. This allows the inputs to be respent.
        """
        return await self._rpc.send_request_async(ABANDON_TRANSACTION, [txid])

    async def abort_rescan(self):
        """
        Stop current wallet rescan triggered by an RPC call, e.g. importprivkey.
        """
        return await self._rpc.send_request_async(ABORT_RESCAN)

    async def add_multisig_address(
        self, nrequired: int, keys: list, label="", address_type=None
    ):
        """
        Add a P2SH or P2WSH multisig address to the wallet.
        """
        params = [nrequired, keys]
        if label:
            params.append(label)
        if address_type:
            params.append(address_type)
        return await self._rpc.send_request_async(ADD_MULTISIG_ADDRESS, params)
