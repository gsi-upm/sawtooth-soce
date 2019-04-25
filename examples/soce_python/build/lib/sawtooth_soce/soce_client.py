# Copyright 2016 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

import hashlib
import base64
from base64 import b64encode
import time
import random
import requests
import yaml

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch

from sawtooth_soce.soce_exceptions import SoceException


def _sha512(data):
    return hashlib.sha512(data).hexdigest()


class SoceClient:
    def __init__(self, base_url, keyfile=None):

        self._base_url = base_url

        if keyfile is None:
            self._signer = None
            return

        try:
            with open(keyfile) as fd:
                private_key_str = fd.read().strip()
        except OSError as err:
            raise SoceException(
                'Failed to read private key {}: {}'.format(
                    keyfile, str(err)))

        try:
            private_key = Secp256k1PrivateKey.from_hex(private_key_str)
        except ParseError as e:
            raise SoceException(
                'Unable to load private key: {}'.format(str(e)))

        self._signer = CryptoFactory(create_context('secp256k1')) \
            .new_signer(private_key)

    def create_voter(self, name, preferences, wait=None, auth_user=None, auth_password=None):
        return self._send_soce_txn(
            "create-voter",
            name_id=name,
            configurations_preferences_id=preferences,
            wait=wait,
            auth_user=auth_user,
            auth_password=auth_password)

    def create_voting(self, name, configurations, sc_method, wait=None, auth_user=None, auth_password=None):
        return self._send_soce_txn(
            action="create-voting",
            name_id=name,
            configurations_preferences_id=configurations,
            sc_method=sc_method,
            wait=wait,
            auth_user=auth_user,
            auth_password=auth_password)

    def register_voter(self, name, voter_id, wait=None, auth_user=None, auth_password=None):
        return self._send_soce_txn(
            action="register-voter",
            name_id=name,
            configurations_preferences_id=voter_id,
            wait=wait,
            auth_user=auth_user,
            auth_password=auth_password)

    def apply_voting_method(self, name, wait=None, auth_user=None, auth_password=None):
        return self._send_soce_txn(
            "apply-voting-method",
            name_id=name,
            wait=wait,
            auth_user=auth_user,
            auth_password=auth_password)

    def _get_status(self, batch_id, wait, auth_user=None, auth_password=None):
        try:
            result = self._send_request(
                'batch_statuses?id={}&wait={}'.format(batch_id, wait),
                auth_user=auth_user,
                auth_password=auth_password)
            return yaml.safe_load(result)['data'][0]['status']
        except BaseException as err:
            raise SoceException(err)

    def _get_prefix(self):
        return _sha512("soce".encode('utf-8'))[0:6]

    def _get_address(self, name):
        soce_prefix = self._get_prefix()
        name_address = _sha512(name.encode('utf-8'))[0:64]
        return soce_prefix + name_address

    def _send_request(self,
                      suffix,
                      data=None,
                      content_type=None,
                      name=None,
                      auth_user=None,
                      auth_password=None):
        if self._base_url.startswith("http://"):
            url = "{}/{}".format(self._base_url, suffix)
        else:
            url = "http://{}/{}".format(self._base_url, suffix)

        headers = {}
        if auth_user is not None:
            auth_string = "{}:{}".format(auth_user, auth_password)
            b64_string = b64encode(auth_string.encode()).decode()
            auth_header = 'Basic {}'.format(b64_string)
            headers['Authorization'] = auth_header

        if content_type is not None:
            headers['Content-Type'] = content_type

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

        return result.text

    def _send_soce_txn(self,
                     action=None, 
                     name_id=None, 
                     configurations_preferences_id=None, 
                     sc_method=None,
                     wait=None,
                     auth_user=None,
                     auth_password=None):
        # Serialization is just a delimited utf-8 encoded string
        payload = ";".join([str(action), str(name_id),
            str(configurations_preferences_id),
            str(sc_method)]).encode()

        # Construct the address
        address = self._get_address(str(name_id))
        address2 = self._get_address(str(configurations_preferences_id))

        header = TransactionHeader(
            signer_public_key=self._signer.get_public_key().as_hex(),
            family_name="soce",
            family_version="1.0",
            inputs=[address, address2],
            outputs=[address, address2],
            dependencies=[],
            payload_sha512=_sha512(payload),
            batcher_public_key=self._signer.get_public_key().as_hex(),
            nonce=hex(random.randint(0, 2**64))
        ).SerializeToString()

        signature = self._signer.sign(header)

        transaction = Transaction(
            header=header,
            payload=payload,
            header_signature=signature
        )

        batch_list = self._create_batch_list([transaction])
        batch_id = batch_list.batches[0].header_signature

        if wait and wait > 0:
            wait_time = 0
            start_time = time.time()
            response = self._send_request(
                "batches", batch_list.SerializeToString(),
                'application/octet-stream',
                auth_user=auth_user,
                auth_password=auth_password)
            while wait_time < wait:
                status = self._get_status(
                    batch_id,
                    wait - int(wait_time),
                    auth_user=auth_user,
                    auth_password=auth_password)
                wait_time = time.time() - start_time

                if status != 'PENDING':
                    return response

            return response

        return self._send_request(
            "batches", batch_list.SerializeToString(),
            'application/octet-stream',
            auth_user=auth_user,
            auth_password=auth_password)

    def _create_batch_list(self, transactions):
        transaction_signatures = [t.header_signature for t in transactions]

        header = BatchHeader(
            signer_public_key=self._signer.get_public_key().as_hex(),
            transaction_ids=transaction_signatures
        ).SerializeToString()

        signature = self._signer.sign(header)

        batch = Batch(
            header=header,
            transactions=transactions,
            header_signature=signature)
        return BatchList(batches=[batch])
