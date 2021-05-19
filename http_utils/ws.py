import websocket
import threading

import gzip
import json
from datetime import datetime
from urllib import parse
import hmac
import base64
from hashlib import sha256
from log.logger import *
import time


class Ws:
    def __init__(self, flag: str, path: str, host: str = None, access_key: str = None, secret_key: str = None):
        self._path = path
        if host is None:
            host = "api.hbdm.vn"
        self._host = host
        self._url = 'wss://{}{}'.format(host, path)
        self._flag = f'{flag}/{self._url}'

        self._ws = None
        self._create_ws()

        self._access_key = access_key
        self._secret_key = secret_key

        self._sub_dict = None
        self._sub_callback = None
        self._req_callback = None
        self._active_close = False

    def __del__(self):
        self.close()

    def _create_ws(self):
        self._ws = None
        self._ws = websocket.WebSocketApp(self._url,
                                          on_open=self._on_open,
                                          on_message=self._on_msg,
                                          on_close=self._on_close,
                                          on_error=self._on_error)
        swt = threading.Thread(
            target=self._ws.run_forever, daemon=True)
        swt.start()
        self._can_work = False
        self._error = False

    def _send_auth_data(self, method: str, path: str, host: str, access_key: str, secret_key: str):
        # timestamp
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

        # get Signature
        suffix = 'AccessKeyId={}&SignatureMethod=HmacSHA256&SignatureVersion=2&Timestamp={}'.format(
            access_key, parse.quote(timestamp))
        payload = '{}{}{}{}'.format(method.upper(), host, path, suffix)

        digest = hmac.new(secret_key.encode('utf8'), payload.encode(
            'utf8'), digestmod=sha256).digest()
        signature = base64.b64encode(digest).decode()

        # data
        data = {
            "op": "auth",
            "type": "api",
            "AccessKeyId": access_key,
            "SignatureMethod": "HmacSHA256",
            "SignatureVersion": "2",
            "Timestamp": timestamp,
            "Signature": signature
        }
        data = json.dumps(data)
        self._ws.send(data)
        logger.debug(data)

    def _on_open(self, ws):
        logger.info(f'ws open in {self._flag}')
        if self._access_key is not None or self._secret_key is not None:
            self._send_auth_data('get', self._path, self._host,
                                 self._access_key, self._secret_key)
        else:
            self._can_work = True
        self.on_open(ws)

    def on_open(self, ws):
        pass

    def _on_msg(self, ws, message):
        try:
            plain = gzip.decompress(message).decode()
            jdata = json.loads(plain)
            if 'ping' in jdata:
                sdata = plain.replace('ping', 'pong')
                self._ws.send(sdata)
            elif 'op' in jdata:
                opdata = jdata['op']
                if opdata == 'ping':
                    sdata = plain.replace('ping', 'pong')
                    self._ws.send(sdata)
                elif opdata == 'auth':
                    if jdata['err-code'] == 0:
                        self._can_work = True
                    logger.info(plain)
                elif opdata == 'sub':
                    logger.info(plain)
                elif opdata == 'unsub':
                    logger.info(plain)
                elif opdata == 'notify':
                    if self._sub_callback is not None:
                        self._sub_callback(jdata)
                else:
                    pass
            elif 'subbed' in jdata:
                logger.info(plain)
            elif 'ch' in jdata:
                if self._sub_callback is not None:
                    self._sub_callback(jdata)
            elif 'rep' in jdata:
                if self._req_callback is not None:
                    self._req_callback(jdata)
                    self._req_callback = None
            else:
                pass
        except Exception as e:
            logger.error(e)
            logger.error(jdata)

    def _on_close(self, ws):
        logger.info(f"ws close in {self._flag}")
        if not self._active_close and self._sub_dict is not None:
            self._create_ws()
            self.sub(self._sub_dict, self._sub_callback)
        else:
            self._error = True
        self.on_close(ws)

    def on_close(self, ws):
        pass

    def _on_error(self, ws, error):
        logger.error(f'error in {self._flag}')
        self._error = True
        self.on_error(ws, error)

    def on_error(self, ws, error):
        pass

    def sub(self, sub_dict: dict, callback):
        while not self._can_work:
            time.sleep(1)
            if self._error:
                logger.error(
                    f'ws error, do not sub: {sub_dict} in {self._flag}')
                return

        self._sub_dict = sub_dict
        self._sub_callback = callback

        sub_str = json.dumps(sub_dict)
        self._ws.send(sub_str)
        logger.info(f'{sub_str} in {self._flag}')

    def unsub(self, unsub_dict: dict):
        while not self._can_work:
            time.sleep(1)
            if self._error:
                logger.error(
                    f'ws error, do not unsub: {sub_dict} in {self._flag}')
                return

        self._sub_dict = None
        self._sub_callback = None

        unsub_str = json.dumps(unsub_dict)
        self._ws.send(unsub_str)
        logger.info(f'{unsub_str} in {self._flag}')

    def req(self, req_dict: dict, callback):
        while not self._can_work:
            time.sleep(1)
            if self._error:
                logger.error(
                    f'ws error, do not req: {sub_dict} in {self._flag}')
                return

        self._req_callback = callback
        req_str = json.dumps(req_dict)
        self._ws.send(req_str)
        logger.info(f'{req_str} in {self._flag}')

    def close(self):
        self._active_close = True
        self._sub_dict = None
        self._sub_callback = None
        self._req_callback = None
        self._ws.close()
