# Copyright 2016-2018 Intel Corporation
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

import logging

from sawtooth_soce.processor.socepy import SocialChoice


from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError

from sawtooth_soce.processor.soce_payload import SocePayload
from sawtooth_soce.processor.soce_state import Voting
from sawtooth_soce.processor.soce_state import Voter
from sawtooth_soce.processor.soce_state import SoceState
from sawtooth_soce.processor.soce_state import SOCE_NAMESPACE


LOGGER = logging.getLogger(__name__)


class SoceTransactionHandler(TransactionHandler):

    @property
    def family_name(self):
        return "soce"

    @property
    def family_versions(self):
        return ['1.0']

    @property
    def namespaces(self):
        return [SOCE_NAMESPACE]

    def apply(self, transaction, context):

        header = transaction.header
        signer = header.signer_public_key

        soce_state = SoceState(context)
        sc = SocialChoice()

        socePayload = SocePayload.from_bytes(transaction.payload)

        action = socePayload.action
        name_id = socePayload.name_id
        configurations_preferences_id = socePayload.configurations_preferences_id
        sc_method = socePayload.sc_method


        if action == 'create-voter':

            preferences = configurations_preferences_id
            if not configurations_preferences_id:
                preferences = {}
            voter = Voter(public_sign = signer, voter_id = name_id, preferences = preferences)
            soce_state.set_voter(name_id, voter)

            _display("Voter with id {} and public sign {}... created.".format(name_id, signer[:6]))


        elif action == 'create-voting':

            voting = Voting(name = name_id, configurations = configurations_preferences_id, sc_method = sc_method)
            soce_state.set_voting(name_id, voting)

            _display("Voting with name {}, social choice method {} and configurations {} created.".format(name_id, sc_method, configurations_preferences_id))


        elif action == 'register-voter':

            voting = soce_state.get_voting(name_id)
            voter = soce_state.get_voter(configurations_preferences_id)
            if voter.preferences.get(name_id):
                preferences = voter.preferences.get(name_id)
            else:
                preferences = dict((el,0) for el in voting.configurations)
                voter.preferences[name_id] = preferences
            voting.preferences[configurations_preferences_id] = preferences
            soce_state.set_voting(name_id, voting)

            _display("Voter with id {} and public sign {}... registered in voting {}.".format(voter.id, signer[:6], name_id))


        elif action == 'unregister-voter':

            voting = soce_state.get_voting(name_id)
            voter = soce_state.get_voter(configurations_preferences_id)
            del voting.preferences[voter.id]
            soce_state.set_voting(name_id, voting)

            _display("Voter with id {} and public sign {}... unregistered from voting {}.".format(voter.id, signer[:6], name_id))


        elif action == 'set-preferences':

            preferences = sc_method
            voter = soce_state.get_voter(configurations_preferences_id)
            voting = soce_state.get_voting(name_id)
            voter.preferences[name_id] = preferences
            voting.preferences[configurations_preferences_id] = preferences
            soce_state.set_voting(name_id, voting)
            soce_state.set_voter(configurations_preferences_id, voter)

            _display("Voter with id {} new preferences on voting {} are {}.".format(configurations_preferences_id, name_id, preferences))


        elif action == 'apply-voting-method':

            voting = soce_state.get_voting(name_id)
            voting_method = voting.method
            preferences = voting.preferences
            print('esto son las preferencias: ', preferences)
            winner = sc.social_choice(voting_method, preferences)
            voting.winner = winner
            voting_name = voting.name
            soce_state.set_voting(voting_name, voting)

            _display("Winner applying {} in voting {} is {}.".format(voting_method, name_id, winner))


        else:
            raise InvalidTransaction('Unhandled action: {}'.format(
                soce_payload.action))


def _display(msg):
    n = msg.count("\n")

    if n > 0:
        msg = msg.split("\n")
        length = max(len(line) for line in msg)
    else:
        length = len(msg)
        msg = [msg]

    # pylint: disable=logging-not-lazy
    LOGGER.debug("+" + (length + 2) * "-" + "+")
    for line in msg:
        LOGGER.debug("+ " + line.center(length) + " +")
    LOGGER.debug("+" + (length + 2) * "-" + "+")