import logging

import pytest

from contract.fee_contract import activate_account
from utils.transaction_util import send_transaction

logger = logging.getLogger()


@pytest.fixture
def random_account(web3, alpha_account):
    account = web3.eth.account.create()
    logger.debug('ACCOUNT[{}, {}]'.format(account.address, account.privateKey.hex()))

    send_funds(web3, alpha_account, account)
    return account


@pytest.fixture
def active_account(web3, fee_contract, random_account):
    account = random_account
    activate_account(web3, account)
    return account


def send_funds(web3, from_account, to_account):
    tx = {
        'to': to_account.address,
        'value': web3.toWei(1, 'ether')
    }
    send_transaction(web3, tx, from_account)
