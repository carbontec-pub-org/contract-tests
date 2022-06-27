import json

import pytest
from eth_account.signers.local import LocalAccount
from web3.constants import HASH_ZERO
from web3.contract import Contract

from contract.fee_contract import activate_account
from utils.transaction_util import send_transaction

KYCCentreRole = "79fce87046aae5e678100c84cc5c4708df4209fab036250bb81408ada9b857ef"
ADMIN_ROLE = "0x0000000000000000000000000000000000000000000000000000000000000000"
_contract: Contract


@pytest.fixture(scope='session')
def kyc_contract(web3) -> Contract:
    with open("./artifacts/KYCContract.abi") as f:
        abi = json.load(f)

    global _contract
    _contract = web3.eth.contract(abi=abi, address="0x0000000000000000000000000000000000001001")
    return _contract


@pytest.fixture
def kyc_centre(web3, contracts_admin) -> LocalAccount:
    centre = web3.eth.account.privateKeyToAccount("ed4c65f1bf6c622f5954ff39932c192b26a963abcc65d56f9487d4cabe9301f1")
    activate_account(web3, centre)
    grant_kyc_centre_role(web3, centre, contracts_admin)
    return centre


@pytest.fixture
def new_kyc_centre(web3, active_account, contracts_admin):
    centre = active_account

    def _new_kyc_centre():
        grant_kyc_centre_role(web3, centre, contracts_admin)
        return centre

    yield _new_kyc_centre
    renounce_kyc_centre_role(web3, centre)


def grant_kyc_centre_role(web3, beneficiary, admin):
    if has_kyc_centre_role(beneficiary):
        return

    tx = _contract.functions.grantRole(KYCCentreRole, beneficiary.address).buildTransaction({
        'from': admin.address,
        'gasPrice': web3.eth.gas_price
    })
    send_transaction(web3, tx, admin)


def renounce_kyc_centre_role(web3, account):
    tx = _contract.functions.renounceRole(KYCCentreRole, account.address).buildTransaction({
        'from': account.address,
        'gasPrice': web3.eth.gas_price
    })
    send_transaction(web3, tx, account)


def has_kyc_centre_role(account: LocalAccount) -> bool:
    return _contract.functions.hasRole(KYCCentreRole, account.address).call()


def create_request(web3, requester, level=1):
    deposit = get_level_price(level)
    tx = _contract.functions.createKYCRequest(level, HASH_ZERO).buildTransaction({
        'from': requester.address,
        'value': deposit,
        'gasPrice': web3.eth.gas_price
    })
    send_transaction(web3, tx, requester)
    return get_global_request_index_of_address(requester.address)


def approve_request(web3, request_index, centre):
    tx = _contract.functions.approveKYCRequest(request_index).buildTransaction({
        'from': centre.address,
        'gasPrice': web3.eth.gas_price
    })
    send_transaction(web3, tx, centre)


def decline_request(web3, request_index, centre):
    tx = _contract.functions.declineRequest(request_index).buildTransaction({
        'from': centre.address,
        'gasPrice': web3.eth.gas_price
    })
    send_transaction(web3, tx, centre)


def withdraw_request(web3, account):
    tx = _contract.functions.repairLostRequest().buildTransaction({
        'from': account.address,
        'gasPrice': web3.eth.gas_price
    })
    send_transaction(web3, tx, account)


def get_level_price(level):
    # return kyc_contract.functions.levelPrices(level).call()
    return level * 1000


def get_user_request(address, index=0):
    request = _contract.functions.viewMyRequest(index).call({'from': address})
    return convert_kyc_request(request)


def get_global_request_index_of_address(address, local_index=0):
    # return _contract.functions.getLastGlobalRequestIndexOfAddress(address).call()
    return _contract.functions.userKYCRequests(address, local_index).call()


def get_payments(address):
    return _contract.functions.payments(address).call()


def convert_kyc_request(request) -> dict:
    return dict({
        'user': request[0],
        'data': request[1],
        'level': request[2],
        'status': request[3],
        'centre': request[4],
        'deposit': request[5]
    })
