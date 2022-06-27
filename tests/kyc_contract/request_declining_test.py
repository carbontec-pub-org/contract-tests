import allure
import pytest
from assertpy import assert_that, soft_assertions
from web3.exceptions import ContractLogicError

from contract.kyc_contract import create_request, get_user_request, approve_request, renounce_kyc_centre_role, \
    get_level_price, get_payments, decline_request
from utils.transaction_util import send_transaction, revert_message


@allure.title("KYC Center can decline pending user's request")
def test_declining_request_by_assigned_centre(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    request_index = create_request(web3, alice)

    tx = kyc_contract.functions.declineRequest(request_index).buildTransaction({
        'from': kyc_centre.address,
        'gasPrice': web3.eth.gas_price
    })
    send_transaction(web3, tx, kyc_centre)

    request = get_user_request(alice.address)
    with soft_assertions():
        assert_that(request['user']).is_equal_to(alice.address)
        assert_that(request['level']).is_equal_to(1)
        assert_that(request['status']).is_equal_to(1)
        assert_that(request['centre']).is_equal_to(kyc_centre.address)


@allure.title("KYC Center can decline approved user's request")
def declining_approved_request(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    request_index = create_request(web3, kyc_contract, alice)
    approve_request(web3, request_index, kyc_centre)

    tx = kyc_contract.functions.declineRequest(request_index).buildTransaction({
        'from': kyc_centre.address,
        'gasPrice': web3.eth.gas_price
    })
    send_transaction(web3, tx, kyc_centre)

    request = get_user_request(alice.address)
    with soft_assertions():
        assert_that(request['user']).is_equal_to(alice.address)
        assert_that(request['level']).is_equal_to(1)
        assert_that(request['status']).is_equal_to(1)
        assert_that(request['centre']).is_equal_to(kyc_centre.address)


def declining_declined_request(web3, kyc_contract, active_account, kyc_centre):
    pass


def declining_withdrawn_request(web3, kyc_contract, active_account, kyc_centre):
    pass


@allure.title("KYC Center receives full deposit when request is declined")
def deposit_transfer_after_request_declining(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    deposit = get_level_price(1)
    old_centre_payments = get_payments(kyc_centre.address)

    index = create_request(web3, alice, 1)
    decline_request(web3, index, kyc_centre)

    centre_payments = get_payments(kyc_centre.address)
    assert (centre_payments - old_centre_payments) == deposit


@allure.title("Account without KYC Center role can't decline request")
def test_declining_request_by_non_kyc_centre(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    request_index = create_request(web3, alice)
    renounce_kyc_centre_role(web3, kyc_centre)

    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.declineRequest(request_index).buildTransaction({
            'from': kyc_centre.address,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted: Not allowed to decline'


@allure.title("KYC Center can't decline request if not assigned for it")
def test_declining_request_by_not_assigned_centre(web3, kyc_contract, active_account, kyc_centre, new_kyc_centre):
    alice = active_account
    request_index = create_request(web3, alice)
    another_kyc_centre = new_kyc_centre()

    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.declineRequest(request_index).buildTransaction({
            'from': another_kyc_centre.address,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted'
