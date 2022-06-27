import pytest
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware


@pytest.fixture(scope='session')
def web3(node):
    web3 = Web3(HTTPProvider(node))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return web3
