from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.types import TxParams, Nonce


def send_transaction(web3: Web3, transaction: TxParams, sender: LocalAccount):
    transaction['nonce'] = _nonce(web3, sender)
    transaction['gas'] = 300_000
    transaction['gasPrice'] = web3.eth.gas_price
    transaction['chainId'] = web3.eth.chain_id
    signed_tx = web3.eth.account.sign_transaction(transaction, sender.privateKey)
    web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_hash = signed_tx['hash'].hex()
    web3.eth.wait_for_transaction_receipt(tx_hash, poll_latency=1.0)
    return tx_hash


def _nonce(web3: Web3, sender: LocalAccount) -> Nonce:
    return web3.eth.get_transaction_count(sender.address)


def error_message(error):
    return error.value.args[0]['message']


def revert_message(error):
    return error.value.args[0]
