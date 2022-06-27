import allure
import pytest
from assertpy import assert_that, soft_assertions

from contract.kyc_contract import create_request, convert_kyc_request, renounce_kyc_centre_role


@allure.title("User can view own request")
def view_own_request_by_user(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    create_request(web3, alice, 1)

    request = kyc_contract.functions.viewMyRequest(0).call({'from': alice.address})

    request = convert_kyc_request(request)
    with soft_assertions():
        assert_that(request['user']).is_equal_to(alice.address)
        assert_that(request['data'].hex()).is_equal_to(64 * '0')
        assert_that(request['level']).is_equal_to(1)
        assert_that(request['status']).is_equal_to(0)
        assert_that(request['centre']).is_equal_to(kyc_centre.address)
        assert_that(request['deposit']).is_equal_to(1000)


@allure.title("User can get last global request index of address")
def get_global_request_index(web3, kyc_contract, active_account, kyc_centre):
    alice = active_account
    expected_index = create_request(web3, alice, 1)

    actual_index = kyc_contract.functions.getLastGlobalRequestIndexOfAddress(alice.address).call()

    assert actual_index == expected_index


@allure.title("User can view request assigned to KYC Center")
def view_request_assigned_to_kyc_centre(web3, kyc_contract, active_account, kyc_centre, new_kyc_centre):
    renounce_kyc_centre_role(web3, kyc_centre)
    centre = new_kyc_centre()

    alice = active_account
    request_index = create_request(web3, alice, 1)

    (request, global_index) = kyc_contract.functions.viewRequestAssignedToCentre(centre.address, 0).call()

    request = convert_kyc_request(request)
    with soft_assertions():
        assert_that(request['user']).is_equal_to(alice.address)
        assert_that(request['data'].hex()).is_equal_to(64 * '0')
        assert_that(request['level']).is_equal_to(1)
        assert_that(request['status']).is_equal_to(0)
        assert_that(request['centre']).is_equal_to(centre.address)
        assert_that(request['deposit']).is_equal_to(1000)
        assert_that(global_index).is_equal_to(request_index)
