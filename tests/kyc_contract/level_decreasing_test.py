import allure
import pytest
from web3.exceptions import ContractLogicError

from contract.kyc_contract import create_request, approve_request, renounce_kyc_centre_role
from utils.transaction_util import send_transaction, revert_message


@allure.title("KYC Center can decrease KYC level of any user")
@pytest.mark.parametrize("decreased_level", [1, 0])
def test_decrease_level_by_kyc_centre(web3, kyc_contract, active_account, kyc_centre, new_kyc_centre, decreased_level):
    alice = active_account
    index = create_request(web3, alice, 2)
    approve_request(web3, index, kyc_centre)
    another_kyc_centre = new_kyc_centre()

    tx = kyc_contract.functions.decreaseKYCLevel(alice.address, decreased_level).buildTransaction({
        'from': another_kyc_centre.address,
        'gasPrice': web3.eth.gas_price
    })
    send_transaction(web3, tx, another_kyc_centre)

    user_level = kyc_contract.functions.level(alice.address).call()
    assert user_level == decreased_level


@allure.title("KYC Center can only decrease the user's KYC level by 'decrease' method")
@pytest.mark.parametrize("increased_level", [1, 2])
def test_increase_level_by_decrease_method(web3, kyc_contract, active_account, kyc_centre, increased_level):
    alice = active_account
    index = create_request(web3, alice, 1)
    approve_request(web3, index, kyc_centre)

    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.decreaseKYCLevel(alice.address, increased_level).buildTransaction({
            'from': kyc_centre.address,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted: You can only decrease level'


@allure.title("Account without KYC Center role can't decrease KYC level of user")
def test_decrease_level_by_non_kyc_centre(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    index = create_request(web3, alice, 2)
    approve_request(web3, index, kyc_centre)
    renounce_kyc_centre_role(web3, kyc_centre)

    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.decreaseKYCLevel(alice.address, 1).buildTransaction({
            'from': kyc_centre.address,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted: Not allowed to set level'
