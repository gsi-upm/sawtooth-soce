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


class SocePayload:

    def __init__(self, payload):
        try:
            # The payload is csv utf-8 encoded string
            action, name_id, configurations_preferences, sc_method = payload.decode().split(",")
        
        except ValueError:
            raise InvalidTransaction("Invalid payload serialization")

        if not name_id:
            raise InvalidTransaction('Name of voting/id of voter is required')

        if '|' in name_id:
            raise InvalidTransaction('Name of voting/id of voter cannot contain "|"')

        if not action:
            raise InvalidTransaction('Action is required')

        if action not in ('create-voter', 'create-voting', 'register-voter', 'apply-voting-method'):
            raise InvalidTransaction('Invalid action: {}'.format(action))


        if action == 'create-voter':
            
            if not configurations_preferences:
                raise InvalidTransaction('Preferences of the voter are required')
            if not type(configurations_preferences) is dict:
                raise InvalidTransaction('Preferences must be a dictionary')

        elif action == 'create-voting':

            if not configurations_preferences:
                raise InvalidTransaction('Configurations to be voted are required')
            if not type(configurations_preferences) is list:
                raise InvalidTransaction('Configurations must be a list')
            
            if not sc_method:
                raise InvalidTransaction('Social choice method is required')


        self._action = action
        self._name_id = name_id
        self._configurations_preferences = configurations_preferences
        self._sc_method = sc_method

    @staticmethod
    def from_bytes(payload):
        return SocePayload(payload=payload)

    @property
    def name(self):
        return self._name

    @property
    def action(self):
        return self._action

    @property
    def space(self):
        return self._space
