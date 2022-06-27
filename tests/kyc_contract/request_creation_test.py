import allure
import pytest
from assertpy import assert_that, soft_assertions
from web3.constants import HASH_ZERO
from web3.exceptions import ContractLogicError

from contract.kyc_contract import get_user_request, create_request, approve_request, renounce_kyc_centre_role, \
    get_level_price
from utils.transaction_util import send_transaction, revert_message


@allure.title("User can create a KYC request to increase own KYC level")
def request_creation(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account

    deposit = get_level_price(1)
    tx = kyc_contract.functions.createKYCRequest(1, HASH_ZERO).buildTransaction({
        'from': alice.address,
        'value': deposit,
        'gasPrice': web3.eth.gas_price
    })
    send_transaction(web3, tx, alice)

    request = get_user_request(alice.address)
    with soft_assertions():
        assert_that(request['user']).is_equal_to(alice.address)
        assert_that(request['data'].hex()).is_equal_to(64 * '0')
        assert_that(request['level']).is_equal_to(1)
        assert_that(request['status']).is_equal_to(0)
        assert_that(request['centre']).is_equal_to(kyc_centre.address)
        assert_that(request['deposit']).is_equal_to(deposit)


@allure.title("User can create KYC request if he doesn't have pending requests")
def request_creation_by_user_with_kyc_level(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    request_index = create_request(web3, alice, 1)
    approve_request(web3, request_index, kyc_centre)

    deposit = get_level_price(2)
    tx = kyc_contract.functions.createKYCRequest(2, HASH_ZERO).buildTransaction({
        'from': alice.address,
        'value': deposit,
        'gasPrice': web3.eth.gas_price
    })
    send_transaction(web3, tx, alice)

    request = get_user_request(alice.address, index=1)
    with soft_assertions():
        assert_that(request['user']).is_equal_to(alice.address)
        assert_that(request['level']).is_equal_to(2)
        assert_that(request['status']).is_equal_to(0)
        assert_that(request['centre']).is_equal_to(kyc_centre.address)
        assert_that(request['deposit']).is_equal_to(deposit)


@allure.title("User receive change if create a KYC request by paying too large deposit")
def overpayment_returns(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account

    # required_deposit = kyc_contract.functions.levelPrices(1).call()
    required_deposit = 0
    overpaid_deposit = 2000
    tx = kyc_contract.functions.createKYCRequest(1, HASH_ZERO).buildTransaction({
        'from': alice.address,
        'value': overpaid_deposit,
        'gasPrice': web3.eth.gas_price
    })
    tx_hash = send_transaction(web3, tx, alice)

    request = get_user_request(alice.address)
    with soft_assertions():
        assert_that(request['user']).is_equal_to(alice.address)
        assert_that(request['deposit']).is_equal_to(required_deposit)

    receipt = web3.eth.get_transaction_receipt(tx_hash)
    estimated_balance = web3.toWei(1, 'ether') - receipt['gasUsed'] * web3.eth.gas_price - (
            overpaid_deposit - required_deposit)
    actual_balance = web3.eth.get_balance(alice.address)
    assert actual_balance == estimated_balance


@allure.title("User can create a KYC request for any greater level")
def request_creation_for_any_greater_level(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    deposit = get_level_price(2)

    tx = kyc_contract.functions.createKYCRequest(2, HASH_ZERO).buildTransaction({
        'from': alice.address,
        'value': deposit,
        'gasPrice': web3.eth.gas_price
    })
    send_transaction(web3, tx, alice)

    request = get_user_request(alice.address)
    with soft_assertions():
        assert_that(request['user']).is_equal_to(alice.address)
        assert_that(request['level']).is_equal_to(2)
        assert_that(request['status']).is_equal_to(0)
        assert_that(request['centre']).is_equal_to(kyc_centre.address)
        assert_that(request['deposit']).is_equal_to(deposit)


@allure.title("User can't create KYC request if he already has requested level")
def test_request_creation_for_already_owned_level(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    request_index = create_request(web3, alice, 1)
    approve_request(web3, request_index, kyc_centre)

    deposit = get_level_price(1)

    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.createKYCRequest(1, HASH_ZERO).buildTransaction({
            'from': alice.address,
            'value': deposit,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted: You already have this KYC level'


@allure.title("User can't create KYC request if he already has greater level")
def test_request_creation_for_lesser_level(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    request_index = create_request(web3, alice, 1)
    approve_request(web3, request_index, kyc_centre)

    deposit = get_level_price(1)

    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.createKYCRequest(0, HASH_ZERO).buildTransaction({
            'from': alice.address,
            'value': deposit,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted: You already have this KYC level'


@allure.title("User can't create a KYC request by paying deposit less than required")
def insufficient_deposit(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    # deposit = get_level_price(1)
    deposit = 0

    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.createKYCRequest(1, HASH_ZERO).buildTransaction({
            'from': alice.address,
            'value': deposit - 1,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted: Provided not enough Ether.'


@allure.title("User can't create KYC request if he has pending request")
def test_repeat_request_creation(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    create_request(web3, alice, 1)

    deposit = get_level_price(1)

    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.createKYCRequest(1, HASH_ZERO).buildTransaction({
            'from': alice.address,
            'value': deposit,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted: Your previous request is still pending answer'


@allure.title("User can't create KYC request if there are no KYC centres")
def test_request_creation_when_no_kyc_centres(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    renounce_kyc_centre_role(web3, kyc_centre)

    deposit = get_level_price(1)

    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.createKYCRequest(1, HASH_ZERO).buildTransaction({
            'from': alice.address,
            'value': deposit,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted: There are no kyc centres'
