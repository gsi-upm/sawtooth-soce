import hashlib
from sawtooth_sdk.processor.exceptions import InternalError
import json
import ast

SOCE_NAMESPACE = hashlib.sha512("soce".encode("utf-8")).hexdigest()[0:6]


def _make_soce_address(name):
    return SOCE_NAMESPACE + \
        hashlib.sha512(name.encode('utf-8')).hexdigest()[:64]


class Voter:
    def __init__(self, public_sign, voter_id = False, preferences = {}):
        self.sign = public_sign
        self.id = voter_id
        self.preferences = preferences

class Voting:
    def __init__(self, name, configurations = [], sc_method = False, winner = False, preferences = {}):
        self.name = name
        self.configurations = configurations
        self.winner = winner
        self.method = sc_method
        self.preferences = preferences


class SoceState:

    TIMEOUT = 3

    def __init__(self, context):

        self._context = context
        self._address_cache = {}

    '''
    def get_voters_preferences(self, voters_id):

        preferences = []
        for voter_id in voters_id:
            voter = self.get_voter(voter_id)
            preferences.append(voter.preferences)
        return preferences
    '''

    def set_voting(self, voting_name, voting):

        votings = self._load_votings(voting_name=voting_name)
        votings[voting_name] = voting
        self._store_voting(voting_name, votings=votings)

    def set_voter(self, voter_id, voter):

        voters = self._load_voters(voter_id=voter_id)
        voters[voter_id] = voter
        self._store_voter(voter_id, voters=voters)

    def get_voting(self, voting_name):

        return self._load_votings(voting_name=voting_name).get(voting_name)

    def get_voter(self, voter_id):

        return self._load_voters(voter_id=voter_id).get(voter_id)

    def delete_voting(self, voting_name):

        votings = self._load_votings(voting_name=voting_name)
        del votings[voting_name]
        if votings:
            self._store_voting(voting_name, votings=votings)
        else:
            self._delete_voting(voting_name)

    def delete_voter(self, voter_id):

        voters = self._load_voters(voter_id=voter_id)
        del voters[voter_id]
        if voters:
            self._store_voter(voter_id, voters=voters)
        else:
            self._delete_voter(voter_id)

    def _store_voting(self, voting_name, votings):

        address = _make_soce_address(voting_name)
        state_data = self._serialize_votings(votings)
        self._address_cache[address] = state_data
        self._context.set_state(
            {address: state_data},
            timeout=self.TIMEOUT)

    def _store_voter(self, voter_id, voters):

        address = _make_soce_address(voter_id)
        state_data = self._serialize_voters(voters)
        self._address_cache[address] = state_data
        self._context.set_state(
            {address: state_data},
            timeout=self.TIMEOUT)

    def _delete_voting(self, voting_name):
        address = _make_soce_address(voting_name)
        self._context.delete_state(
            [address],
            timeout=self.TIMEOUT)
        self._address_cache[address] = None

    def _delete_voter(self, voter_id):
        address = _make_soce_address(voter_id)
        self._context.delete_state(
            [address],
            timeout=self.TIMEOUT)
        self._address_cache[address] = None

    def _load_votings(self, voting_name):
        address = _make_soce_address(voting_name)
        if address in self._address_cache:
            if self._address_cache[address]:
                serialized_votings = self._address_cache[address]
                votings = self._deserialize_votings(serialized_votings)
            else:
                votings = {}
        else:
            state_entries = self._context.get_state(
                [address],
                timeout=self.TIMEOUT)
            if state_entries:
                self._address_cache[address] = state_entries[0].data
                votings = self._deserialize_votings(data=state_entries[0].data)
            else:
                self._address_cache[address] = None
                votings = {}
        return votings

    def _load_voters(self, voter_id):
        address = _make_soce_address(voter_id)
        if address in self._address_cache:
            if self._address_cache[address]:
                serialized_voters = self._address_cache[address]
                voters = self._deserialize_voters(serialized_voters)
            else:
                voters = {}
        else:
            state_entries = self._context.get_state(
                [address],
                timeout=self.TIMEOUT)
            if state_entries:
                self._address_cache[address] = state_entries[0].data
                voters = self._deserialize_voters(data=state_entries[0].data)
            else:
                self._address_cache[address] = None
                voters = {}
        return voters

    def _serialize_preferences(self, preferences):
        p1 =  preferences
        p2 = {}
        for k, v in p1.items():
            p2[k] = json.dumps(v)
        p3 = json.dumps(p2)
        return p3

    def _deserialize_preferences(self, preferences):
        p1 = ast.literal_eval(preferences)
        p2 = {}
        print('preferences: ', preferences)
        if isinstance(p1, str):
            return {}
        for k, v in p1.items():
            print('key: ', k, 'valor: ', v)
            if  isinstance(v, dict):
                p2[k] = v
            else:
                p2[k] = ast.literal_eval(v)
        print('preferences 2: ', p2)
        return p2

    def _deserialize_votings(self, data):

        votings = {}
        for voting in data.decode().split("|"):
            name, configurations, sc_method, winner, preferences = voting.split(";")
            votings[name] = Voting(name, ast.literal_eval(configurations), 
                sc_method, winner, self._deserialize_preferences(preferences))
        return votings

    def _deserialize_voters(self, data):

        voters = {}
        for voter in data.decode().split("|"):
            name, voter_id, preferences = voter.split(";")
            voters[name] = Voter(name, voter_id, self._deserialize_preferences(preferences))
        return voters

    def _serialize_votings(self, votings):

        votings_strs = []
        for name, voting in votings.items():
            voting_strs = ";".join(
                [name, str(voting.configurations), 
                str(voting.method), str(voting.winner), 
                json.dumps(voting.preferences)])
            votings_strs.append(voting_strs)
        return "|".join(sorted(votings_strs)).encode()

    def _serialize_voters(self, voters):

        voters_strs = []
        for name, voter in voters.items():
            voter_strs = ";".join(
                [name, str(voter.id), json.dumps(voter.preferences)])
            voters_strs.append(voter_strs)
        return "|".join(sorted(voters_strs)).encode()