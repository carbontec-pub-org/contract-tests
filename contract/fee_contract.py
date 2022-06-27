import json

import pytest
from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.contract import Contract

from utils.transaction_util import send_transaction

_contract: Contract


@pytest.fixture(autouse=True, scope='session')
def fee_contract(web3) -> Contract:
    with open("./artifacts/FeeContract.abi") as f:
        abi = json.load(f)

    global _contract
    _contract = web3.eth.contract(abi=abi, address="0x0000000000000000000000000000000000001000")
    return _contract


def activate_account(web3: Web3, account: LocalAccount):
    is_active = _contract.functions.paidFee(account.address).call()
    if is_active:
        return
    fee = _contract.functions.initialFee().call()
    tx = _contract.functions.pay().buildTransaction({
        'from': account.address,
        'value': fee,
        'gasPrice': web3.eth.gas_price
    })
    send_transaction(web3, tx, account)
