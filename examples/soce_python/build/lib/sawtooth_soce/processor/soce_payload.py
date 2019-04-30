# Copyright 2018 Intel Corporation
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
# -----------------------------------------------------------------------------

from sawtooth_sdk.processor.exceptions import InvalidTransaction

import ast

class SocePayload:

    def __init__(self, payload):

        print('PAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOAD', payload)
        actions = ['create-voter', 'create-voting', 'register-voter', 'unregister-voter', 'apply-voting-method', 'set-preferences', 'get-entity-info', 'get-all-info']

        try:
            print(payload)
            print(payload.decode())
            # The payload is csv utf-8 encoded string
            action, name_id, configurations_preferences_id, sc_method = payload.decode().split(";")
        
        except ValueError:

            print('PAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOAD', type(payload))
            print('PAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOAD', payload)
            print('PAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOADPAYLOAD', payload.decode())
            raise InvalidTransaction("Invalid payload serialization")

        if not action:
            raise InvalidTransaction('Action is required')

        if action not in actions:
            raise InvalidTransaction('Invalid action: {}'.format(action))

        if not name_id:
            raise InvalidTransaction('Name of voting/id of voter is required')

        if '|' in name_id or ';' in name_id:
            raise InvalidTransaction('Name of voting/id of voter cannot contain "|" or ";" ')


        if action == 'create-voter':
            
            if not configurations_preferences_id:
                raise InvalidTransaction('Preferences of the voter are required')
            if not type(ast.literal_eval(configurations_preferences_id)) is dict:
                raise InvalidTransaction('Preferences must be a dictionary')

        elif action == 'create-voting':

            if not configurations_preferences_id:
                raise InvalidTransaction('Configurations to be voted are required')
            if not type(ast.literal_eval(configurations_preferences_id)) is list:
                raise InvalidTransaction('Configurations must be a list')
            
            if not sc_method:
                raise InvalidTransaction('Social choice method is required')


        elif action == 'register-voter':

            if not configurations_preferences_id:
                raise InvalidTransaction('Id of the voter is required')


        self._action = action
        self._name_id = name_id
        self._configurations_preferences_id = configurations_preferences_id
        self._sc_method = sc_method

    @staticmethod
    def from_bytes(payload):
        return SocePayload(payload=payload)


    @property
    def action(self):
        return self._action

    @property
    def name_id(self):
        return self._name_id

    @property
    def configurations_preferences_id(self):
        return self._configurations_preferences_id

    @property
    def sc_method(self):
        return self._sc_method
