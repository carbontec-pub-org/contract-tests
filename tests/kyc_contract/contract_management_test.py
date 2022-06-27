import allure
import pytest
from web3.exceptions import ContractLogicError

from utils.transaction_util import send_transaction, revert_message


@allure.title("Admin of KYC Contract can change KYC level price")
def set_level_price_by_admin(web3, kyc_contract, contracts_admin):
    new_price = 999
    tx = kyc_contract.functions.setLevelPrice(1, new_price).buildTransaction({
        'from': contracts_admin.address,
        'gasPrice': web3.eth.gas_price
    })
    send_transaction(web3, tx, contracts_admin)

    actual_price = kyc_contract.functions.levelPrices(1).call()
    assert actual_price == new_price


@allure.title("Non-admin of KYC Contract can't change KYC level price")
def test_set_level_price_by_non_admin(web3, kyc_contract, active_account):
    alice = active_account
    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.setLevelPrice(1, 999).buildTransaction({
            'from': alice.address,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted'
