import json

def _deserialize_votings(data):

    votings = {}
    try:
        for voting in data.decode().split("|"):
            name, value = voting.split(";")
            votings[name] = Voting(name, value.configurations, value.sc_method, value.winner, value.voters)
    except ValueError:
        raise InternalError("Failed to deserialize voting data")
    return votings

def _deserialize_voters(data):

    voters = {}
    try:
        for voter in data.decode().split("|"):
            name, value = voter.split(";")
            voters[name] = Voter(sign, value.preferences)
    except ValueError:
        raise InternalError("Failed to deserialize voting data")
    return voters

def _serialize_votings(votings):

    votings_strs = []
    for name, voting in votings.items():
        voting_strs = ",".join(
            [name, json.dumps(voting.configurations), str(voting.method), str(voting.winner), json.dumps(voting.voters)])
        votings_strs.append(voting_strs)
    return "|".join(sorted(votings_strs)).encode()


def _serialize_voters(voters):

    voters_strs = []
    for sign, voter in voters.items():
        voter_strs = ",".join(
            [sign, json.dumps(voter.preferences)])
        voters_strs.append(voter_strs)
    return "|".join(sorted(voters_strs)).encode()

class Voter:
    def __init__(self, public_sign, preferences = {}):
        self.sign = public_sign
        self.preferences = preferences

class Voting:
    def __init__(self, name, configurations = [], sc_method = False, winner = False, voters = []):
        self.name = name
        self.configurations = configurations
        self.winner = winner
        self.method = sc_method
        self.voters = voters


v1 = Voter('1', {'a': 1, 'b': 2})

v2 = Voter('2', {'a': 2, 'b': 1})

v = Voting('voting', ['a', 'b'], 'borda', False, [v1.sign, v2.sign])



a = _serialize_votings({v.name: v})

b = _serialize_voters({v1.sign: v1, v2.sign: v2})


print(a)

print(b)


c = _serialize_votings({v.name: v})

d = _serialize_voters({v1.sign: v1, v2.sign: v2})


print(c)

print(d)