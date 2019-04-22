# Copyright 2017 Intel Corporation
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

from sawtooth_processor_test.message_factory import MessageFactory


class SoceMessageFactory:
    def __init__(self, signer=None):
        self._factory = MessageFactory(
            family_name="soce",
            family_version="1.0",
            namespace=MessageFactory.sha512("soce".encode("utf-8"))[0:6],
            signer=signer)

    def _voting_to_address(self, votingName):
        return self._factory.namespace + \
            self._factory.sha512(votingName.encode())[0:64]

    def create_tp_register(self):
        return self._factory.create_tp_register()

    def create_tp_response(self, status):
        return self._factory.create_tp_response(status)

    def _create_txn(self, txn_function, votingName, action, value=None):
        payload = ",".join([
            str(votingName), str(action), str(value)
        ]).encode()

        addresses = [self._voting_to_address(votingName)]

        return txn_function(payload, addresses, addresses, [])

    def create_tp_process_request(self, action, votingName, value=None):
        txn_function = self._factory.create_tp_process_request
        return self._create_txn(txn_function, votingName, action, value)

    def create_transaction(self, votingName, action, value=None):
        txn_function = self._factory.create_transaction
        return self._create_txn(txn_function, votingName, action, value)

    def create_get_request(self, votingName):
        addresses = [self._voting_to_address(votingName)]
        return self._factory.create_get_request(addresses)

    def create_get_response(self, votingName, value = None):
        address = self._voting_to_address(votingName)

        data = None
        if value is not None:
            data = ",".join([votingName, value]).encode()
        else:
            data = None

        return self._factory.create_get_response({address: data})

    def create_set_request(self, votingName, value = None):
        address = self._voting_to_address(votingName)

        data = None
        if value is not None:
            data = ",".join([votingName, value]).encode()
        else:
            data = None

        return self._factory.create_set_request({address: data})

    def create_set_response(self, votingName):
        addresses = [self._voting_to_address(votingName)]
        return self._factory.create_set_response(addresses)

    def get_public_key(self):
        return self._factory.get_public_key()
