import allure
import pytest
from web3.exceptions import ContractLogicError

from utils.transaction_util import send_transaction, error_message, revert_message

initial_fee = 1000


@allure.title("User with an inactive account can't send funds")
def test_inactive_account_cant_send_funds(web3, random_account, alpha_account):
    alice = random_account
    tx = {
        'from': alice.address,
        'to': alpha_account.address,
        'value': 1000
    }

    with pytest.raises(ValueError) as error:
        send_transaction(web3, tx, alice)

    assert error_message(error) == 'account not activated'


@allure.title("User can activate account by paying activation fee")
def test_account_activation(web3, random_account, fee_contract):
    alice = random_account
    tx = fee_contract.functions.pay().buildTransaction({
        'from': alice.address,
        'value': 1000,
        'gasPrice': web3.eth.gas_price
    })

    send_transaction(web3, tx, alice)

    activated = fee_contract.functions.paidFee(alice.address).call()
    assert activated is True


@allure.title("User receive change if activate account by paying too large fee")
def overpayment_returns(web3, random_account, fee_contract):
    alice = random_account
    overpaid_fee = 2000
    tx = fee_contract.functions.pay().buildTransaction({
        'from': alice.address,
        'value': overpaid_fee,
        'gasPrice': web3.eth.gas_price
    })

    tx_hash = send_transaction(web3, tx, alice)

    activated = fee_contract.functions.paidFee(alice.address).call()
    assert activated is True

    receipt = web3.eth.get_transaction_receipt(tx_hash)
    estimated_balance = web3.toWei(1, 'ether') - receipt['gasUsed'] * web3.eth.gas_price - (overpaid_fee - initial_fee)
    actual_balance = web3.eth.get_balance(alice.address)
    assert actual_balance == estimated_balance


@allure.title("User can't activate account by paying fee less than required")
def insufficient_fee(web3, random_account, fee_contract):
    alice = random_account

    with pytest.raises(ContractLogicError) as error:
        fee_contract.functions.pay().buildTransaction({
            'from': alice.address,
            'value': (initial_fee - 1),
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted: Provided not enough Ether.'


@allure.title("Owner of Fee Contract can change activation fee")
def change_fee_by_owner(web3, contracts_admin, fee_contract):
    new_fee = 500

    tx = fee_contract.functions.changeFee(new_fee).buildTransaction({
        'from': contracts_admin.address,
        'gasPrice': web3.eth.gas_price
    })

    send_transaction(web3, tx, contracts_admin)

    actual_fee = fee_contract.functions.initialFee().call()
    assert actual_fee == new_fee


@allure.title("Non-owner of Fee Contract can't change activation Fee")
def test_change_fee_by_non_owner(web3, random_account, fee_contract):
    alice = random_account
    new_fee = 500

    with pytest.raises(ContractLogicError) as error:
        fee_contract.functions.changeFee(new_fee).buildTransaction({
            'from': alice.address,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted: Ownable: caller is not the owner'
