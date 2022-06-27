import allure
import pytest
from assertpy import assert_that, soft_assertions
from web3.exceptions import ContractLogicError

from contract.kyc_contract import create_request, renounce_kyc_centre_role, get_user_request, approve_request, \
    decline_request, withdraw_request, get_payments, get_level_price
from utils.transaction_util import send_transaction, revert_message


@allure.title("User can withdraw pending KYC request, if assigned KYC Center lose KYC-Center role")
def test_withdrawal_pending_request(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    create_request(web3, alice, 1)
    renounce_kyc_centre_role(web3, kyc_centre)

    tx = kyc_contract.functions.repairLostRequest().buildTransaction({
        'from': alice.address,
        'gasPrice': web3.eth.gas_price
    })
    send_transaction(web3, tx, alice)

    request = get_user_request(alice.address)
    with soft_assertions():
        assert_that(request['user']).is_equal_to(alice.address)
        assert_that(request['level']).is_equal_to(1)
        assert_that(request['status']).is_equal_to(3)
        assert_that(request['centre']).is_equal_to(kyc_centre.address)


@allure.title("Requester receives full deposit when request is withdrawn")
def deposit_transfer_after_request_withdrawal(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    deposit = get_level_price(1)

    create_request(web3, alice, 1)
    renounce_kyc_centre_role(web3, kyc_centre)
    withdraw_request(web3, alice)

    alice_payments = get_payments(alice.address)
    assert alice_payments == deposit


@allure.title("User can't withdraw pending KYC request, if assigned KYC Center still have KYC-Center role")
def test_withdrawal_request_with_active_kyc_centre(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    create_request(web3, alice, 1)

    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.repairLostRequest().buildTransaction({
            'from': alice.address,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted: Your KYC centre is still active'


@allure.title("User can't withdraw approved KYC request")
def test_withdrawal_approved_request(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    index = create_request(web3, alice, 1)
    approve_request(web3, index, kyc_centre)
    renounce_kyc_centre_role(web3, kyc_centre)

    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.repairLostRequest().buildTransaction({
            'from': alice.address,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted: Your last request cannot be repaired'


@allure.title("User can't withdraw declined KYC request")
def test_withdrawal_declined_request(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    index = create_request(web3, alice, 1)
    decline_request(web3, index, kyc_centre)
    renounce_kyc_centre_role(web3, kyc_centre)

    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.repairLostRequest().buildTransaction({
            'from': alice.address,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted: Your last request cannot be repaired'


@allure.title("User can't withdraw already withdrawn KYC request")
def test_withdrawal_withdrawn_request(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    create_request(web3, alice, 1)
    renounce_kyc_centre_role(web3, kyc_centre)
    withdraw_request(web3, alice)

    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.repairLostRequest().buildTransaction({
            'from': alice.address,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted: Your last request cannot be repaired'
