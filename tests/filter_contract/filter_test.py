import allure
import pytest

from contract.filter_contract import get_filter_level, set_filter_level
from contract.kyc_contract import create_request, approve_request
from utils.transaction_util import send_transaction, error_message


@pytest.fixture
def account_with_kyc_level(web3, kyc_contract, kyc_centre, active_account):
    def account_with_kyc_level(level):
        index = create_request(web3, active_account, level)
        approve_request(web3, index, kyc_centre)
        return active_account

    return account_with_kyc_level


@pytest.fixture
def account_with_filter_level(web3, filter_contract, active_account):
    def account_with_filter_level(level):
        set_filter_level(web3, active_account, level)
        return active_account

    return account_with_filter_level


@allure.title("User can send funds to another user by default")
def test_user_sends_funds_by_default(web3, active_account, alpha_account):
    alice = active_account

    tx = {
        'to': alpha_account.address,
        'value': web3.toWei(0.1, 'ether')
    }
    tx_hash = send_transaction(web3, tx, alice)

    receipt = web3.eth.get_transaction_receipt(tx_hash)
    assert receipt['status'] == 1


@allure.title("User can set filter level")
@pytest.mark.parametrize("level", [0, 1])
def test_set_filter_level(web3, filter_contract, active_account, level):
    alice = active_account

    tx = filter_contract.functions.setFilterLevel(level).buildTransaction({
        'from': alice.address,
        'gasPrice': web3.eth.gas_price
    })
    send_transaction(web3, tx, alice)

    assert get_filter_level(alice) == level


@allure.title("User with sufficient KYC level can send funds to another user with configured filter")
def test_send_funds_to_user_with_filter(web3, account_with_kyc_level, account_with_filter_level):
    alice = account_with_kyc_level(1)
    bob = account_with_filter_level(1)

    tx = {
        'to': bob.address,
        'value': web3.toWei(0.1, 'ether')
    }
    tx_hash = send_transaction(web3, tx, alice)

    receipt = web3.eth.get_transaction_receipt(tx_hash)
    assert receipt['status'] == 1


@allure.title("User with high KYC level can send funds to user with configured filter")
def test_user_with_high_kyc_level_sends_funds(web3, account_with_kyc_level, account_with_filter_level):
    alice = account_with_kyc_level(2)
    bob = account_with_filter_level(1)

    tx = {
        'to': bob.address,
        'value': web3.toWei(0.1, 'ether')
    }
    tx_hash = send_transaction(web3, tx, alice)

    receipt = web3.eth.get_transaction_receipt(tx_hash)
    assert receipt['status'] == 1


@allure.title("User with insufficient KYC level can't send funds to user with configured filter")
def test_user_with_insufficient_kyc_level_sends_funds(web3, active_account, account_with_filter_level):
    alice = active_account
    bob = account_with_filter_level(1)
    tx = {
        'to': bob.address,
        'value': web3.toWei(0.1, 'ether')
    }

    with pytest.raises(ValueError) as error:
        send_transaction(web3, tx, alice)
    assert error_message(error) == 'kyc level too low'


@allure.title("User can get own filter level")
def test_get_own_filter_level(web3, filter_contract, account_with_filter_level):
    alice = account_with_filter_level(1)

    actual_level = filter_contract.functions.viewFilterLevel().call({'from': alice.address})

    assert actual_level == 1


@allure.title("User check that a transfer from sender address to destination address will be rejected by nodes")
def test_check_transfer_will_be_rejected(web3, filter_contract, account_with_kyc_level, account_with_filter_level):
    alice = account_with_kyc_level(1)
    bob = account_with_filter_level(2)

    is_not_rejected = filter_contract.functions.filter(alice.address, bob.address).call()

    assert is_not_rejected is False


@allure.title("User can check that a transfer from sender address to destination address won't be rejected by nodes")
@pytest.mark.parametrize("kyc_level", [1, 2])
def test_check_transfer_will_not_be_rejected(web3, filter_contract, account_with_kyc_level,
                                             account_with_filter_level, kyc_level):
    alice = account_with_kyc_level(kyc_level)
    bob = account_with_filter_level(1)

    is_not_rejected = filter_contract.functions.filter(alice.address, bob.address).call()

    assert is_not_rejected is True
