import pytest

from bitbridge.rpc.wallet import WalletSync
from bitbridge.rpc.raw_transaction import RawTransactionSync
from bitbridge.rpc.generate import GenerateSync
from bitbridge.rpc.util import UtilSync


@pytest.fixture
def wallet_sync(rpc_delegate_sync):
    return WalletSync(rpc_delegate_sync)


@pytest.fixture
def raw_transaction_sync(rpc_delegate_sync):
    return RawTransactionSync(rpc_delegate_sync)


@pytest.fixture
def generate_sync(rpc_delegate_sync):
    return GenerateSync(rpc_delegate_sync)


@pytest.fixture
def util_sync(rpc_delegate_sync):
    return UtilSync(rpc_delegate_sync)


@pytest.fixture
def wallet_created_sync(wallet_sync):
    wallet_sync.create_wallet(wallet_name="test_wallet")
    from_address = wallet_sync.get_new_address(label="test_from_address")
    to_address = wallet_sync.get_new_address(label="test_to_address")

    from_address = from_address.get("result")
    to_address = to_address.get("result")
    return from_address, to_address


@pytest.fixture
def from_address_sync(fake, wallet_sync):
    response = wallet_sync.get_new_address(label=fake.word())
    return response.get("result")


@pytest.fixture
def to_address_sync(fake, wallet_sync):
    response = wallet_sync.get_new_address(label=fake.word())
    return response.get("result")


@pytest.fixture
def generate_to_address_sync(generate_sync, wallet_created_sync):
    from_address_sync, to_address_sync = wallet_created_sync
    generate_sync.generate_to_address(101, from_address_sync)


@pytest.fixture
def transaction_sync(
    wallet_sync,
    raw_transaction_sync,
    wallet_created_sync,
    generate_to_address_sync,
):
    from_address_sync, to_address_sync = wallet_created_sync
    amount = 0.00001
    unspent_txs = wallet_sync.list_unspent()
    inputs = [
        {"txid": tx["txid"], "vout": tx["vout"]}
        for tx in unspent_txs["result"]
        if tx["address"] == from_address_sync
    ]

    # Prepare outputs for the transaction
    outputs = {to_address_sync: amount}

    # Create the raw transaction
    raw_tx = raw_transaction_sync.create_raw_transaction(inputs, outputs)

    # Sign the raw transaction
    signed_tx = raw_transaction_sync.signraw_transaction_with_wallet(raw_tx["result"])
    # Broadcast the transaction to the network
    tx_id = raw_transaction_sync.send_raw_transaction(
        signed_tx["result"]["hex"], maxfeerate=1000
    )

    return tx_id.get("result")


def test_abandon_transaction(wallet_sync, transaction_sync):
    result = wallet_sync.abandon_transaction(transaction_sync)
    assert result, "Expected a non-empty result"
    assert "result" in result, "Expected 'result' key in the response"


def test_abort_rescan(wallet_sync):
    result = wallet_sync.abort_rescan()
    assert result, "Expected a non-empty result"
    assert "result" in result, "Expected 'result' key in the response"


@pytest.mark.skip(reason="Only legacy wallets are supported by this command")
def test_add_multisig_address(wallet_sync, util_sync):
    # Generate two new addresses
    address1 = wallet_sync.get_new_address()["result"]
    address2 = wallet_sync.get_new_address()["result"]

    # Obtain the public keys associated with the addresses using getaddressinfo
    pubkey1 = wallet_sync.get_address_info(address1)["result"]["scriptPubKey"]
    pubkey2 = wallet_sync.get_address_info(address2)["result"]["scriptPubKey"]

    # Use the public keys to create a multisig address
    nrequired = 2
    keys = [pubkey1, pubkey2]
    label = "test_label"
    result = wallet_sync.add_multisig_address(nrequired, keys, label)

    # Assertions
    assert result, "Expected a non-empty result"
    assert "result" in result, "Expected 'result' key in the response"
