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

    def voting_voter_to_address(self, name_id):
        return self._factory.namespace + \
            self._factory.sha512(name_id.encode())[0:64]

    def create_tp_register(self):
        return self._factory.create_tp_register()

    def create_tp_response(self, status):
        return self._factory.create_tp_response(status)

    def _create_txn(self, txn_function, action = None, name_id = None, configurations_preferences_id = None, sc_method = None):
        
        payload = ";".join([
           str(action), str(name_id), str(configurations_preferences_id), str(sc_method)
        ]).encode()

        print('txn en camino!', payload)
        
        addresses = [self.voting_voter_to_address(name_id), self.voting_voter_to_address(configurations_preferences_id)]

        return txn_function(payload, addresses, addresses, [])

    def create_tp_process_request(self, action = None, name_id = None, configurations_preferences_id = None, sc_method = None):
        txn_function = self._factory.create_tp_process_request
        return self._create_txn(txn_function, action, name_id, configurations_preferences_id, sc_method)

    def create_transaction(self, action = None, name_id = None, configurations_preferences_id = None, sc_method = None):
        txn_function = self._factory.create_transaction
        return self._create_txn(txn_function, action, name_id, configurations_preferences_id, sc_method)

    def create_get_request(self, name_id):
        addresses = [self.voting_voter_to_address(name_id)]
        return self._factory.create_get_request(addresses)

    def create_get_response(self, name_id, value = None):
        address = self.voting_voter_to_address(name_id)

        data = None
        if value is not None:
            data = ";".join([name_id, value]).encode()
        else:
            data = None

        return self._factory.create_get_response({address: data})

    def create_set_request(self, action = None, name_id = None, configurations_preferences = None, sc_method = None):
        address = self.voting_voter_to_address(name_id)

        print('create_set_request')
        data = None
        if value is not None:
            data = ";".join([str(action), str(name_id), str(configurations_preferences), str(sc_method)]).encode()
        else:
            data = None

        return self._factory.create_set_request({address: data})

    def create_set_response(self, name_id):
        addresses = [self.voting_voter_to_address(name_id)]
        return self._factory.create_set_response(addresses)

    def get_public_key(self):
        return self._factory.get_public_key()
