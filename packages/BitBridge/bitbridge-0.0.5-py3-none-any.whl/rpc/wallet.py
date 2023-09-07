from bitbridge.rpc.base_rpc import BaseRPC
from bitbridge.utils.constants import (
    ABANDON_TRANSACTION,
    ABORT_RESCAN,
    ADD_MULTISIG_ADDRESS,
    GET_NEW_ADDRESS,
    GET_ADDRESS_INFO,
    CREATE_WALLET,
    LOAD_WALLET,
    UNLOAD_WALLET,
    GET_WALLET_INFO,
    LIST_UNSPENT,
    LIST_WALLETS,
    LIST_WALLET_DIR,
    GET_BALANCE,
    GET_BALANCES,
    GET_TRANSACTION,
    SEND_TO_ADDRESS,
)


class BaseWallet(BaseRPC):
    pass


class WalletSync(BaseWallet):
    def abandon_transaction(self, txid: str):
        return self.rpc_delegate.send_request(ABANDON_TRANSACTION, [txid])

    def list_wallets(self):
        return self.rpc_delegate.send_request(LIST_WALLETS)

    def list_wallet_dir(self):
        return self.rpc_delegate.send_request(LIST_WALLET_DIR)

    def abort_rescan(self):
        return self.rpc_delegate.send_request(ABORT_RESCAN)

    def add_multisig_address(self, nrequired: int, keys: list, label: str = None):
        return self.rpc_delegate.send_request(
            ADD_MULTISIG_ADDRESS, [nrequired, keys, label]
        )

    def create_wallet(
        self,
        wallet_name: str,
        disable_private_keys: bool = False,
        blank: bool = False,
        passphrase: str = None,
        avoid_reuse: bool = True,
        descriptors: bool = True,
        load_on_startup: bool = True,
    ):
        return self.rpc_delegate.send_request(
            CREATE_WALLET,
            [
                wallet_name,
                disable_private_keys,
                blank,
                passphrase,
                avoid_reuse,
                descriptors,
                load_on_startup,
            ],
        )

    def get_new_address(
        self, label: str = None, address_type: str = None, append_to_url: str = None
    ):
        return self.rpc_delegate.send_request(
            GET_NEW_ADDRESS, [label, address_type], append_to_url=append_to_url
        )

    def get_address_info(self, address: str):
        return self.rpc_delegate.send_request(GET_ADDRESS_INFO, [address])

    def load_wallet(self, wallet_name: str):
        return self.rpc_delegate.send_request(LOAD_WALLET, [wallet_name])

    def unload_wallet(self, wallet_name: str):
        return self.rpc_delegate.send_request(UNLOAD_WALLET, [wallet_name])

    def get_wallet_info(self):
        return self.rpc_delegate.send_request(GET_WALLET_INFO)

    def list_unspent(
        self, minconf: int = 1, maxconf: int = 9999999, addresses: list = None
    ):
        return self.rpc_delegate.send_request(
            LIST_UNSPENT, [minconf, maxconf, addresses]
        )

    def get_balance(self, minconf: int = 0, include_watchonly: bool = False):
        return self.rpc_delegate.send_request(
            GET_BALANCE, ["*", minconf, include_watchonly]
        )

    def get_balances(self, minconf: int = 1, include_watchonly: bool = False):
        return self.rpc_delegate.send_request(
            GET_BALANCES, [minconf, include_watchonly]
        )

    def get_transaction(
        self, txid: str, include_watchonly: bool = False, verbose: bool = False
    ):
        return self.rpc_delegate.send_request(
            GET_TRANSACTION, [txid, include_watchonly, verbose]
        )

    def send_to_address(
        self,
        address: str,
        amount: float,
        comment: str = None,
        comment_to: str = None,
        subtractfeefromamount: bool = False,
        replaceable: bool = False,
        conf_target: int = None,
        estimate_mode: str = None,
    ):
        return self.rpc_delegate.send_request(
            SEND_TO_ADDRESS,
            [
                address,
                amount,
                comment,
                comment_to,
                subtractfeefromamount,
                replaceable,
                conf_target,
                estimate_mode,
            ],
        )


class WalletAsync(BaseWallet):
    async def abandon_transaction(self, txid: str):
        return await self.rpc_delegate.send_request_async(ABANDON_TRANSACTION, [txid])

    async def list_wallets(self):
        return await self.rpc_delegate.send_request_async(LIST_WALLETS)

    async def list_wallet_dir(self):
        return await self.rpc_delegate.send_request_async(LIST_WALLET_DIR)

    async def abort_rescan(self):
        return await self.rpc_delegate.send_request_async(ABORT_RESCAN)

    async def add_multisig_address(self, nrequired: int, keys: list, label: str = None):
        return await self.rpc_delegate.send_request_async(
            ADD_MULTISIG_ADDRESS, [nrequired, keys, label]
        )

    async def get_new_address(
        self, label: str = None, address_type: str = None, append_to_url: str = None
    ):
        return await self.rpc_delegate.send_request_async(
            GET_NEW_ADDRESS, [label, address_type], append_to_url=append_to_url
        )

    async def get_wallet_info(self):
        return await self.rpc_delegate.send_request_async(GET_WALLET_INFO)

    async def list_unspent(
        self, minconf: int = 1, maxconf: int = 9999999, addresses: list = None
    ):
        return await self.rpc_delegate.send_request_async(
            LIST_UNSPENT, [minconf, maxconf, addresses]
        )

    async def create_wallet(
        self,
        wallet_name: str,
        disable_private_keys: bool = False,
        blank: bool = False,
        passphrase: str = None,
        avoid_reuse: bool = True,
        descriptors: bool = True,
        load_on_startup: bool = True,
    ):
        return await self.rpc_delegate.send_request_async(
            CREATE_WALLET,
            [
                wallet_name,
                disable_private_keys,
                blank,
                passphrase,
                avoid_reuse,
                descriptors,
                load_on_startup,
            ],
        )

    async def get_address_info(self, address: str):
        return await self.rpc_delegate.send_request_async(GET_ADDRESS_INFO, [address])

    async def load_wallet(self, wallet_name: str):
        return await self.rpc_delegate.send_request_async(LOAD_WALLET, [wallet_name])

    async def unload_wallet(self, wallet_name: str):
        return await self.rpc_delegate.send_request_async(UNLOAD_WALLET, [wallet_name])

    async def get_balance(self, minconf: int = 1, include_watchonly: bool = False):
        return await self.rpc_delegate.send_request_async(
            GET_BALANCE, [minconf, include_watchonly]
        )

    async def get_balances(self, minconf: int = 1, include_watchonly: bool = False):
        return await self.rpc_delegate.send_request_async(
            GET_BALANCES, [minconf, include_watchonly]
        )

    async def get_transaction(
        self, txid: str, include_watchonly: bool = False, verbose: bool = False
    ):
        return await self.rpc_delegate.send_request_async(
            GET_TRANSACTION, [txid, include_watchonly, verbose]
        )

    async def send_to_address(
        self,
        address: str,
        amount: float,
        comment: str = None,
        comment_to: str = None,
        subtractfeefromamount: bool = False,
        replaceable: bool = False,
        conf_target: int = None,
        estimate_mode: str = None,
    ):
        return await self.rpc_delegate.send_request_async(
            SEND_TO_ADDRESS,
            [
                address,
                amount,
                comment,
                comment_to,
                subtractfeefromamount,
                replaceable,
                conf_target,
                estimate_mode,
            ],
        )
