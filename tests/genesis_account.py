import pytest


@pytest.fixture(scope='session')
def alpha_account(web3):
    return web3.eth.account.privateKeyToAccount('16bd6f1fafed1f1f1ae9d27db97064589be7207946735225782f5726f4195f85')


@pytest.fixture(scope='session')
def contracts_admin(web3):
    return web3.eth.account.privateKeyToAccount('4f3432f05f0f66fc2ba987acc522499ee29bc20201617a54cc5f992549a3ce65')
