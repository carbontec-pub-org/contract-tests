import allure
import pytest
from assertpy import soft_assertions, assert_that
from web3.exceptions import ContractLogicError

from contract.kyc_contract import get_user_request, renounce_kyc_centre_role, \
    approve_request, create_request, decline_request, withdraw_request, grant_kyc_centre_role, get_level_price, \
    get_payments
from utils.transaction_util import send_transaction, revert_message


@allure.title("KYC Center can approve request if assigned for it")
def test_approving_request_by_assigned_centre(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    request_index = create_request(web3, alice)

    tx = kyc_contract.functions.approveKYCRequest(request_index).buildTransaction({
        'from': kyc_centre.address,
        'gasPrice': web3.eth.gas_price
    })
    send_transaction(web3, tx, kyc_centre)

    request = get_user_request(alice.address)
    user_level = kyc_contract.functions.level(alice.address).call()
    with soft_assertions():
        assert_that(request['user']).is_equal_to(alice.address)
        assert_that(request['level']).is_equal_to(1)
        assert_that(request['status']).is_equal_to(2)
        assert_that(request['centre']).is_equal_to(kyc_centre.address)
        assert_that(user_level).is_equal_to(1)


@allure.title("Requester and KYC Center receive half of deposit when request is approved")
def deposit_transfer_after_request_approving(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    deposit = get_level_price(1)
    old_centre_payments = get_payments(kyc_centre.address)

    index = create_request(web3, alice, 1)
    approve_request(web3, index, kyc_centre)

    alice_payments = get_payments(alice.address)
    centre_payments = get_payments(kyc_centre.address)
    with soft_assertions():
        assert_that(alice_payments).is_equal_to(deposit / 2)
        assert_that(centre_payments - old_centre_payments).is_equal_to(deposit / 2)


@allure.title("Account without KYC Center role can't approve request")
def test_approving_request_by_non_kyc_centre(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    request_index = create_request(web3, alice)
    renounce_kyc_centre_role(web3, kyc_centre)

    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.approveKYCRequest(request_index).buildTransaction({
            'from': kyc_centre.address,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted: Not allowed to approve'


@allure.title("KYC Center can't approve request if not assigned for it")
def test_approving_request_by_not_assigned_centre(web3, kyc_contract, active_account, kyc_centre, new_kyc_centre):
    alice = active_account
    request_index = create_request(web3, alice)
    another_kyc_centre = new_kyc_centre()

    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.approveKYCRequest(request_index).buildTransaction({
            'from': another_kyc_centre.address,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted'


@allure.title("KYC Center can't approve already approved request")
def test_approving_approved_request(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    request_index = create_request(web3, alice)
    approve_request(web3, request_index, kyc_centre)

    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.approveKYCRequest(request_index).buildTransaction({
            'from': kyc_centre.address,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted: This request is not pending decision'


@allure.title("KYC Center can't approve declined request")
def test_approving_declined_request(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    request_index = create_request(web3, alice, 1)
    decline_request(web3, request_index, kyc_centre)

    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.approveKYCRequest(request_index).buildTransaction({
            'from': kyc_centre.address,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted: This request is not pending decision'


@allure.title("KYC Center can't approve withdrawn request")
def test_approving_withdrawn_request(web3, kyc_contract, active_account, kyc_centre, contracts_admin):
    alice = active_account
    request_index = create_request(web3, alice, 1)
    renounce_kyc_centre_role(web3, kyc_centre)
    withdraw_request(web3, alice)
    grant_kyc_centre_role(web3, kyc_centre, contracts_admin)

    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.approveKYCRequest(request_index).buildTransaction({
            'from': kyc_centre.address,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted: This request is not pending decision'
