from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from hashlib import sha512
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
import cbor
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
import urllib.request
from urllib.error import HTTPError
import hashlib
import requests
import yaml
from base64 import b64encode
import hashlib
import base64
from base64 import b64encode
import time
import random
import requests
import yaml

DISTRIBUTION_NAME = 'sawtooth-soce'
DEFAULT_URL = 'http://127.0.0.1:8008'

def _get_address(name):
    soce_prefix = _get_prefix()
    name_address = _sha512(name.encode('utf-8'))[0:64]
    return soce_prefix + name_address

def _sha512(data):
    print('data', data)
    print(1, hashlib.sha512(data))
    print(2, hashlib.sha512(data).hexdigest())
    return hashlib.sha512(data).hexdigest()

def _get_prefix():
    print(4, "soce".encode('utf-8'))
    print(3, _sha512("soce".encode('utf-8'))[0:6])

    return _sha512("soce".encode('utf-8'))[0:6]

def _send_request(suffix,
                      data=None,
                      content_type=None,
                      name=None,
                      auth_user=None,
                      auth_password=None):
        if DEFAULT_URL.startswith("http://"):
            url = "{}/{}".format(DEFAULT_URL, suffix)
        else:
            url = "http://{}/{}".format(DEFAULT_URL, suffix)

        headers = {}
        if auth_user is not None:
            auth_string = "{}:{}".format(auth_user, auth_password)
            b64_string = b64encode(auth_string.encode()).decode()
            auth_header = 'Basic {}'.format(b64_string)
            headers['Authorization'] = auth_header

        if content_type is not None:
            headers['Content-Type'] = content_type

        print('url', url)
        
        try:
            if data is not None:
                result = requests.post(url, headers=headers, data=data)
            else:
                result = requests.get(url, headers=headers)

            if result.status_code == 404:
                raise SoceException("No such resource: {}".format(name))

            if not result.ok:
                raise SoceException("Error {}: {}".format(
                    result.status_code, result.reason))

        except requests.ConnectionError as err:
            raise SoceException(
                'Failed to connect to {}: {}'.format(url, str(err)))

        except BaseException as err:
            raise SoceException(err)
        print(result.text)
        return result.text


def get_entity_info(name, auth_user=None, auth_password=None):
    address = _get_address(name)
    result = _send_request(
        "state/{}".format(address),
        name=name,
        auth_user=auth_user,
        auth_password=auth_password)
    return base64.b64decode(yaml.safe_load(result)["data"])


def get_all_info(auth_user=None, auth_password=None):
    soce_prefix = _get_prefix()
    print(soce_prefix)
    result = _send_request(
        "state?address={}".format(soce_prefix),
        auth_user=auth_user,
        auth_password=auth_password)
    encoded_entries = yaml.safe_load(result)["data"]
    return [base64.b64decode(entry["data"]) for entry in encoded_entries]

print(get_all_info())
print(get_entity_info('voting1'))

