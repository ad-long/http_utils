import requests
from urllib import parse
import json
from datetime import datetime
import hmac
import base64
from hashlib import sha256
from log.logger import *


def get(host: str, path: str, params: dict = None) -> tuple:
    '''
    return: (True, data)/(False, msg)
    '''
    try:
        url = 'https://{}{}'.format(host, path)
        logger.info(url)
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        res = requests.get(url, params=params, headers=headers, timeout=30)
        data = res.json()
        if data['status'] != 'ok':
            msg = data['status']
            if 'err_msg' in data:
                msg = data['err_msg']
            return False, msg
    except Exception as e:
        return False, str(e)
    return True, data


def get_url_suffix(method: str, access_key: str, secret_key: str, host: str, path: str) -> str:
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    timestamp = parse.quote(timestamp)
    suffix = 'AccessKeyId={}&SignatureMethod=HmacSHA256&SignatureVersion=2&Timestamp={}'.format(
        access_key, timestamp)
    payload = '{}\n{}\n{}\n{}'.format(method.upper(), host, path, suffix)

    digest = hmac.new(secret_key.encode('utf8'), payload.encode(
        'utf8'), digestmod=sha256).digest()
    signature = base64.b64encode(digest).decode()

    suffix = '{}&Signature={}'.format(suffix, parse.quote(signature))
    return suffix


def post(access_key: str, secret_key: str, host: str, path: str, data: dict = None) -> tuple:
    '''
    return: (True, data)/(False, msg)
    '''
    try:
        url = 'https://{}{}?{}'.format(host, path, get_url_suffix('post', access_key, secret_key, host, path))
        logger.info(url)
        headers = {'Accept': 'application/json',
                   'Content-type': 'application/json'}
        res = requests.post(url, json=data, headers=headers)
        data = res.json()
        if data['status'] != 'ok':
            return False, data['err_msg']
    except Exception as e:
        return False, str(e)
    return True, data
