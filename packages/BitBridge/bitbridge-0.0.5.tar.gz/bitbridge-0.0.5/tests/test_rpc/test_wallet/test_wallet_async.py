import pytest

from bitbridge.rpc.wallet import WalletAsync
from bitbridge.rpc.raw_transaction import RawTransactionAsync
from bitbridge.rpc.generate import GenerateAsync
from bitbridge.rpc.util import UtilAsync


@pytest.fixture
def wallet_async(rpc_delegate_async):
    return WalletAsync(rpc_delegate_async)


@pytest.fixture
def raw_transaction_async(rpc_delegate_async):
    return RawTransactionAsync(rpc_delegate_async)


@pytest.fixture
def generate_async(rpc_delegate_async):
    return GenerateAsync(rpc_delegate_async)


@pytest.fixture
def util_async(rpc_delegate_async):
    return UtilAsync(rpc_delegate_async)


@pytest.fixture
async def wallet_created_async(fake, wallet_async):
    wallet = await wallet_async.create_wallet(wallet_name=fake.word())
    wallet_name = wallet.get("result").get("name")
    from_address = await wallet_async.get_new_address(
        label=fake.word(), append_to_url=wallet_name
    )
    to_address = await wallet_async.get_new_address(
        label=fake.word(), append_to_url=wallet_name
    )
    from_address = from_address.get("result")
    to_address = to_address.get("result")
    return from_address, to_address


@pytest.fixture
async def generate_to_address_async(generate_async, wallet_created_async):
    from_address_async, to_address_async = wallet_created_async

    await generate_async.generate_to_address(101, from_address_async)
    await generate_async.generate_to_address(101, to_address_async)


@pytest.fixture
async def transaction_async(
    wallet_async,
    raw_transaction_async,
    wallet_created_async,
    generate_to_address_async,
):
    from_address_async, to_address_async = wallet_created_async
    amount = 0.00001
    unspent_txs = await wallet_async.list_unspent()
    inputs = [
        {"txid": tx["txid"], "vout": tx["vout"]}
        for tx in unspent_txs["result"]
        if tx["address"] == from_address_async
    ]

    # Prepare outputs for the transaction
    outputs = {to_address_async: amount}

    # Create the raw transaction
    raw_tx = await raw_transaction_async.create_raw_transaction(inputs, outputs)

    # Sign the raw transaction
    signed_tx = await raw_transaction_async.signraw_transaction_with_wallet(
        raw_tx["result"]
    )

    # Broadcast the transaction to the network
    tx_id = await raw_transaction_async.send_raw_transaction(
        signed_tx["result"]["hex"], maxfeerate=1000
    )

    return tx_id.get("result")


async def test_abandon_transaction(wallet_async, transaction_async):
    result = await wallet_async.abandon_transaction(transaction_async)
    assert result, "Expected a non-empty result"
    assert "result" in result, "Expected 'result' key in the response"
