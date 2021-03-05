import sys
import unittest
from config import *
import time

sys.path.append('..')
from http_utils.ws import *
from http_utils.logger import *

class TestWs(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def _callback_1(self, jdata):
        logger.info('_callback_1:{}'.format(jdata))

    def _callback_2(self, jdata):
        logger.info('_callback_2:{}'.format(jdata))

    def test_sub(self):
        ws1 = Ws("/linear-swap-ws")
        ch = "market.BTC-USDT.kline.1min"
        req = {"sub": ch}
        ws1._sub(req, self._callback_1)

        ws2 = Ws("/linear-swap-ws")
        ch = "market.ETH-USDT.kline.1min"
        req = {"sub": ch}
        ws2._sub(req, self._callback_2)

        time.sleep(10)
        ws1.close()
        ws2.close()

    def test_req(self):
        ws1 = Ws("/linear-swap-ws")
        ch = "market.BTC-USDT.kline.1min"
        req = {"req": ch, "from": 1614320780, "to": 1614321780}
        ws1._req(req, self._callback_1)

        ws2 = Ws("/linear-swap-ws")
        ch = "market.ETH-USDT.kline.1min"
        req = {"req": ch, "from": 1614320780, "to": 1614321780}
        ws2._req(req, self._callback_2)

        time.sleep(10)
        ws1.close()
        ws2.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
