import sys
import unittest
from config import *

sys.path.append('..')
from http_utils.rest import *
from http_utils.logger import *


class TestRest(unittest.TestCase):
    def test_get(self):
        result = get(config['host'], '/linear-swap-api/v1/swap_contract_info', {'contract_code': 'BTC-USDT'})
        logger.info(result)
        self.assertEqual('ok', result['status'])

    def test_post(self):
        result = post(config['access_key'], config['secret_key'], config['host'],
                      '/linear-swap-api/v1/swap_cross_account_info', {'margin_account': 'USDT'})
        logger.info(result)
        self.assertEqual('ok', result['status'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
