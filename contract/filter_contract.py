import json

import pytest
from web3.contract import Contract

from utils.transaction_util import send_transaction

_contract: Contract


@pytest.fixture(autouse=True, scope='session')
def filter_contract(web3) -> Contract:
    with open("./artifacts/FilterContract.abi") as f:
        abi = json.load(f)

    global _contract
    _contract = web3.eth.contract(abi=abi, address="0x0000000000000000000000000000000000001002")
    return _contract


def set_filter_level(web3, account, level):
    tx = _contract.functions.setFilterLevel(level).buildTransaction({
        'from': account.address,
        'gasPrice': web3.eth.gas_price
    })
    send_transaction(web3, tx, account)


def get_filter_level(account):
    return _contract.functions.viewFilterLevel().call({'from': account.address})
