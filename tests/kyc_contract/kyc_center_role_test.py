import allure
import pytest
from assertpy import soft_assertions, assert_that
from web3.exceptions import ContractLogicError

from contract.kyc_contract import KYCCentreRole, renounce_kyc_centre_role, has_kyc_centre_role, ADMIN_ROLE
from utils.transaction_util import send_transaction, revert_message


@pytest.fixture
def role_beneficiary(web3, active_account):
    yield active_account
    renounce_kyc_centre_role(web3, active_account)


@allure.title("User with KYC-Center admin role can grant KYC-Center role")
def test_grant_role_by_role_admin(web3, kyc_contract, role_beneficiary, contracts_admin):
    tx = kyc_contract.functions.grantRole(KYCCentreRole, role_beneficiary.address).buildTransaction({
        'from': contracts_admin.address,
        'gasPrice': web3.eth.gas_price
    })
    send_transaction(web3, tx, contracts_admin)

    assert has_kyc_centre_role(role_beneficiary) is True


@allure.title("User without KYC-Center admin role can't grant KYC-Center role")
def test_grant_role_by_not_role_admin(web3, kyc_contract, active_account, alpha_account):
    alice = alpha_account
    bob = active_account

    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.grantRole(KYCCentreRole, bob.address).buildTransaction({
            'from': alice.address,
            'gasPrice': web3.eth.gas_price
        })
    with soft_assertions():
        assert_that(revert_message(error)).is_equal_to_ignoring_case(
            'execution reverted: AccessControl: account {} is missing role {}'.format(alice.address, ADMIN_ROLE))
        assert_that(has_kyc_centre_role(bob)).is_false()


@allure.title("User with KYC-Center admin role can revoke KYC-Center role")
def test_revoke_role_by_role_admin(web3, kyc_contract, kyc_centre, contracts_admin):
    tx = kyc_contract.functions.revokeRole(KYCCentreRole, kyc_centre.address).buildTransaction({
        'from': contracts_admin.address,
        'gasPrice': web3.eth.gas_price
    })
    send_transaction(web3, tx, contracts_admin)

    assert has_kyc_centre_role(kyc_centre) is False


@allure.title("User without KYC-Center admin role can't revoke KYC-Center role")
def test_revoke_role_by_not_role_admin(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account

    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.revokeRole(KYCCentreRole, kyc_centre.address).buildTransaction({
            'from': alice.address,
            'gasPrice': web3.eth.gas_price
        })
    with soft_assertions():
        assert_that(revert_message(error)).is_equal_to_ignoring_case(
            'execution reverted: AccessControl: account {} is missing role {}'.format(alice.address, ADMIN_ROLE))
        assert_that(has_kyc_centre_role(kyc_centre)).is_true()


@allure.title("User with KYC-Center role can renounce KYC-Center role for self")
def test_renounce_role_for_self(web3, kyc_contract, kyc_centre):
    tx = kyc_contract.functions.renounceRole(KYCCentreRole, kyc_centre.address).buildTransaction({
        'from': kyc_centre.address,
        'gasPrice': web3.eth.gas_price
    })
    send_transaction(web3, tx, kyc_centre)

    assert has_kyc_centre_role(kyc_centre) is False


@allure.title("User with KYC-Center role can't renounce KYC-Center role for another user")
def test_renounce_role_for_another_user(web3, kyc_contract, kyc_centre, active_account):
    alice = active_account

    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.renounceRole(KYCCentreRole, kyc_centre.address).buildTransaction({
            'from': alice.address,
            'gasPrice': web3.eth.gas_price
        })
    assert revert_message(error) == 'execution reverted: AccessControl: can only renounce roles for self'


@allure.title("User can find out KYC-Center admin role")
def test_find_out_admin_role(web3, kyc_contract):
    role = kyc_contract.functions.getRoleAdmin(KYCCentreRole).call()

    assert role.hex() == 64 * '0'


@allure.title("User can find out number of accounts that have KYC-Center role")
def test_find_out_number_of_kyc_centres(web3, kyc_contract, kyc_centre, new_kyc_centre):
    new_kyc_centre()

    number = kyc_contract.functions.getRoleMemberCount(KYCCentreRole).call()

    assert number == 2


@allure.title("User can find out number of accounts that have KYC-Center role when no one has such role")
def test_find_out_number_of_kyc_centres_when_no_centres(web3, kyc_contract, kyc_centre):
    renounce_kyc_centre_role(web3, kyc_centre)

    number = kyc_contract.functions.getRoleMemberCount(KYCCentreRole).call()

    assert number == 0


@allure.title("User can find out one of accounts that have KYC-Center role")
def test_find_out_account_with_role(web3, kyc_contract, kyc_centre, new_kyc_centre):
    another_kyc_centre = new_kyc_centre()

    first_centre = kyc_contract.functions.getRoleMember(KYCCentreRole, 0).call()
    second_centre = kyc_contract.functions.getRoleMember(KYCCentreRole, 1).call()

    with soft_assertions():
        assert_that(first_centre).is_equal_to(kyc_centre.address)
        assert_that(second_centre).is_equal_to(another_kyc_centre.address)


@allure.title("User can't get one of accounts that have KYC-Center role by incorrect index")
def test_find_out_account_with_role_by_incorrect_index(web3, kyc_contract, kyc_centre):
    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.getRoleMember(KYCCentreRole, 1).call()
    assert revert_message(error) == 'execution reverted'


@allure.title("User can't get one of accounts that have KYC-Center role if no one has such role")
def test_find_out_account_with_role_when_no_one_has_role(web3, kyc_contract, kyc_centre):
    renounce_kyc_centre_role(web3, kyc_centre)

    with pytest.raises(ContractLogicError) as error:
        kyc_contract.functions.getRoleMember(KYCCentreRole, 0).call()
    assert revert_message(error) == 'execution reverted'


@allure.title("User can check if account has KYC-Center role")
def test_check_account_has_role(web3, kyc_contract, kyc_centre):
    has_role = kyc_contract.functions.hasRole(KYCCentreRole, kyc_centre.address).call()

    assert has_role is True


@allure.title("User can check if account don't have KYC-Center role")
def test_check_account_do_not_have_role(web3, kyc_contract, kyc_centre):
    renounce_kyc_centre_role(web3, kyc_centre)

    has_role = kyc_contract.functions.hasRole(KYCCentreRole, kyc_centre.address).call()

    assert has_role is False
