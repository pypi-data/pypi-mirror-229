from utils.constants import ABANDON_TRANSACTION, ABORT_RESCAN, ADD_MULTISIG_ADDRESS


class WalletSync:
    def __init__(self, base_rpc):
        self._rpc = base_rpc

    def abandon_transaction(self, txid: str):
        """
        Mark in-wallet transaction <txid> as abandoned. This allows the inputs to be respent.
        """
        return self._rpc.send_request(ABANDON_TRANSACTION, [txid])

    def abort_rescan(self):
        """
        Stop current wallet rescan triggered by an RPC call, e.g. importprivkey.
        """
        return self._rpc.send_request(ABORT_RESCAN)

    def add_multisig_address(
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
        return self._rpc.send_request(ADD_MULTISIG_ADDRESS, params)
