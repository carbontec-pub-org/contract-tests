import allure
import pytest
from assertpy import soft_assertions, assert_that

from contract.kyc_contract import create_request, approve_request, get_payments, get_level_price, \
    get_global_request_index_of_address
from utils.transaction_util import send_transaction


@pytest.fixture
def another_account(active_account):
    return active_account


@allure.title("User can withdraw 'refunded' payments from KYC contract for own address")
def test_withdrawal_payments_for_own_address(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    index = create_request(web3, alice, 1)
    approve_request(web3, index, kyc_centre)
    old_balance = web3.eth.get_balance(alice.address)
    payment = get_payments(alice.address)

    tx = kyc_contract.functions.withdrawPayments(alice.address).buildTransaction({
        'from': alice.address,
        'gasPrice': web3.eth.gas_price
    })
    tx_hash = send_transaction(web3, tx, alice)

    receipt = web3.eth.get_transaction_receipt(tx_hash)
    estimated_balance = old_balance - receipt['gasUsed'] * web3.eth.gas_price + payment
    actual_balance = web3.eth.get_balance(alice.address)
    with soft_assertions():
        assert_that(actual_balance).is_equal_to(estimated_balance)
        assert_that(get_payments(alice.address)).is_zero()


@allure.title("User can withdraw 'refunded' payments from KYC contract for any address")
def test_withdrawal_payments_for_any_address(web3, kyc_contract, active_account, another_account, kyc_centre):
    alice = active_account
    bob = another_account
    index = create_request(web3, bob, 1)
    approve_request(web3, index, kyc_centre)
    old_balance = web3.eth.get_balance(bob.address)
    payment = get_payments(bob.address)

    tx = kyc_contract.functions.withdrawPayments(bob.address).buildTransaction({
        'from': alice.address,
        'gasPrice': web3.eth.gas_price
    })
    tx_hash = send_transaction(web3, tx, alice)

    receipt = web3.eth.get_transaction_receipt(tx_hash)
    estimated_balance = old_balance - receipt['gasUsed'] * web3.eth.gas_price + payment
    actual_balance = web3.eth.get_balance(alice.address)
    with soft_assertions():
        assert_that(actual_balance).is_equal_to(estimated_balance)
        assert_that(get_payments(bob.address)).is_zero()


@allure.title("User can withdraw zero amount of 'refunded' payments from KYC contract")
def test_withdrawal_zero_payments(web3, kyc_contract, active_account):
    alice = active_account
    old_balance = web3.eth.get_balance(alice.address)

    tx = kyc_contract.functions.withdrawPayments(alice.address).buildTransaction({
        'from': alice.address,
        'gasPrice': web3.eth.gas_price
    })
    tx_hash = send_transaction(web3, tx, alice)

    receipt = web3.eth.get_transaction_receipt(tx_hash)
    estimated_balance = old_balance - receipt['gasUsed'] * web3.eth.gas_price
    actual_balance = web3.eth.get_balance(alice.address)
    with soft_assertions():
        assert_that(actual_balance).is_equal_to(estimated_balance)
        assert_that(get_payments(alice.address)).is_zero()


@allure.title("User can view owed zero payments to own address")
def test_view_owed_zero_payments_to_own_address(web3, kyc_contract, active_account):
    alice = active_account

    payments = kyc_contract.functions.payments(alice.address).call()

    assert payments == 0


@allure.title("User can view owed payments to own address")
def view_owed_payments_to_own_address(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    index = create_request(web3, alice, 1)
    approve_request(web3, index, kyc_centre)

    payments = kyc_contract.functions.payments(alice.address).call()

    assert payments == get_level_price(1) / 2


@allure.title("User can view owed payments after several requests")
def view_owed_payments_after_several_requests(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    index_one = create_request(web3, alice, 1)
    approve_request(web3, index_one, kyc_centre)

    create_request(web3, alice, 2)
    index_two = get_global_request_index_of_address(alice.address, 1)
    approve_request(web3, index_two, kyc_centre)

    payments = kyc_contract.functions.payments(alice.address).call()

    assert payments == (get_level_price(1) + get_level_price(2)) / 2
