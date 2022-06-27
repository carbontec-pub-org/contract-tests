import pytest

pytest_plugins = [
    'contract.fee_contract',
    'contract.kyc_contract',
    'contract.filter_contract',
    'tests.context',
    'tests.genesis_account',
    'utils.account_util'
]


def pytest_addoption(parser):
    parser.addoption('--node', default='http://localhost:8575')


@pytest.fixture(scope='session', autouse=True)
def node(request):
    return request.config.getoption("--node")
