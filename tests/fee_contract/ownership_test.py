import allure
import pytest
from web3.constants import ADDRESS_ZERO
from web3.exceptions import ContractLogicError

from utils.transaction_util import send_transaction, revert_message


@pytest.fixture
def new_owner(web3, random_account, fee_contract, contracts_admin):
    yield random_account
    tx = fee_contract.functions.transferOwnership(contracts_admin.address).buildTransaction({
        'from': random_account.address,
        'gasPrice': web3.eth.gas_price
    })
    send_transaction(web3, tx, random_account)


@allure.title("User can find out who is the owner of contract")
def test_find_out_contract_owner(fee_contract):
    owner = fee_contract.functions.owner().call()

    assert owner == '0x0000000000000000000000000000000000001007'


@allure.title("Owner of Fee Contract can transfer ownership")
def transfer_ownership_by_owner(web3, new_owner, contracts_admin, fee_contract):
    alice = new_owner
    tx = fee_contract.functions.transferOwnership(alice.address).buildTransaction({
        'from': contracts_admin.address,
        'gasPrice': web3.eth.gas_price
    })

    send_transaction(web3, tx, contracts_admin)

    actual_owner = fee_contract.functions.owner().call()
    assert actual_owner == alice.address


@allure.title("Owner of Fee Contract can't transfer ownership to zero address")
def transfer_ownership_to_zero_address(web3, contracts_admin, fee_contract):
    with pytest.raises(ContractLogicError) as error:
        fee_contract.functions.transferOwnership(ADDRESS_ZERO).buildTransaction({
            'from': contracts_admin.address,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted: Ownable: new owner is the zero address'


@allure.title("Non-owner of Fee Contract can't transfer ownership")
def test_transfer_ownership_by_non_owner(web3, alpha_account, fee_contract):
    alice = alpha_account

    with pytest.raises(ContractLogicError) as error:
        fee_contract.functions.transferOwnership(alice.address).buildTransaction({
            'from': alice.address,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted: Ownable: caller is not the owner'


@allure.title("Non-owner of Fee Contract can't renounce ownership")
def test_renounce_ownership_by_non_owner(web3, alpha_account, fee_contract):
    alice = alpha_account

    with pytest.raises(ContractLogicError) as error:
        fee_contract.functions.renounceOwnership().buildTransaction({
            'from': alice.address,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted: Ownable: caller is not the owner'


@allure.title("Owner of Fee Contract can renounce ownership")
def renounce_ownership_by_owner(web3, contracts_admin, fee_contract):
    estimate_gas = fee_contract.functions.renounceOwnership().estimateGas({
        'from': contracts_admin.address,
        'gasPrice': web3.eth.gas_price
    })

    assert estimate_gas is not None
