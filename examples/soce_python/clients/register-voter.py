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

def _sha512(data):
    return hashlib.sha512(data).hexdigest()

def _get_prefix():
    return _sha512("soce".encode('utf-8'))[0:6]

def _get_address(name):
    soce_prefix = _get_prefix()
    name_address = _sha512(name.encode('utf-8'))[0:64]
    return soce_prefix + name_address

context = create_context('secp256k1')
private_key = context.new_random_private_key()
signer = CryptoFactory(context).new_signer(private_key)


action = 'register-voter'
name_id = 'voter1'
configurations_preferences_id = 'voting1'
sc_method = {}

payload = {
    'action': action,
    'name_id': name_id,
    'configurations_preferences_id': configurations_preferences_id,
    'sc_method': sc_method
}

address = _get_address(str(name_id))
address2 = _get_address(str(configurations_preferences_id))

#payload_bytes = cbor.dumps(payload)

payload_bytes = ";".join([str(action), str(name_id),
            str(configurations_preferences_id),
            str(None)]).encode()

txn_header_bytes = TransactionHeader(
    family_name='soce',
    family_version='1.0',
    inputs=[address, address2],
    outputs=[address, address2],
    signer_public_key = signer.get_public_key().as_hex(),
    # In this example, we're signing the batch with the same private key,
    # but the batch can be signed by another party, in which case, the
    # public key will need to be associated with that key.
    batcher_public_key = signer.get_public_key().as_hex(),
    # In this example, there are no dependencies.  This list should include
    # an previous transaction header signatures that must be applied for
    # this transaction to successfully commit.
    # For example,
    # dependencies=['540a6803971d1880ec73a96cb97815a95d374cbad5d865925e5aa0432fcf1931539afe10310c122c5eaae15df61236079abbf4f258889359c4d175516934484a'],
    dependencies=[],
    payload_sha512=sha512(payload_bytes).hexdigest()
).SerializeToString()

signature = signer.sign(txn_header_bytes)

txn = Transaction(
    header=txn_header_bytes,
    header_signature=signature,
    payload=payload_bytes
)

txns = [txn]

batch_header_bytes = BatchHeader(
    signer_public_key=signer.get_public_key().as_hex(),
    transaction_ids=[txn.header_signature for txn in txns],
).SerializeToString()

signature = signer.sign(batch_header_bytes)

batch = Batch(
    header=batch_header_bytes,
    header_signature=signature,
    transactions=txns
)

batch_list_bytes = BatchList(batches=[batch]).SerializeToString()

try:
    request = urllib.request.Request(
        'http://localhost:8008/batches',
        batch_list_bytes,
        method='POST',
        headers={'Content-Type': 'application/octet-stream'})
    response = urllib.request.urlopen(request)

except HTTPError as e:
    response = e.file