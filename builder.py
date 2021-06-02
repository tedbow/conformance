"""
Contains a class to help build fixtures programmatically.
"""

from securesystemslib import formats, signer
from tuf import repository_tool

import json
import os
import shutil
import sys


class FixtureBuilder:

    def __init__(self):
        my_dir = self.dir()
        my_name = os.path.basename(my_dir)

        # The index of the next key pair (in the keys/ directory) to use when initializing
        # a role.
        self._key_index = 0
        # The public keys, indexed by role name.
        self.public_keys = {}
        # The private keys, indexed by role name.
        self.private_keys = {}
        # The directory of server-side metadata (and targets).
        self._server_dir = os.path.join(my_dir, 'server')
        # The directory of client-side metadata.
        self._client_dir = os.path.join(my_dir, 'client')

        # If a directory of server-side metadata already exists, remove it.
        if os.path.isdir(self._server_dir):
            shutil.rmtree(self._server_dir)

        # If a directory of client-side metadata already exists, remove it.
        if os.path.isdir(self._client_dir):
            shutil.rmtree(self._client_dir)

        self.repository = repository_tool.create_new_repository(self._server_dir, my_name)
        self.repository.status()

        # Initialize the basic TUF roles.
        self._initialize_role('root')
        self._initialize_role('targets')
        self._initialize_role('snapshot')
        self._initialize_role('timestamp')

        self.repository.status()

    def _initialize_role(self, role_name):
        (public_key, private_key) = self._import_key(role_name)

        role = getattr(self.repository, role_name)
        role.add_verification_key(public_key)
        role.load_signing_key(private_key)

        self.public_keys[role_name] = public_key
        self.private_keys[role_name] = private_key

        self.repository.mark_dirty([role_name])

    def _import_key(self, role_name):
        keys_dir = os.path.join(os.path.dirname(__file__), 'keys')
        private_key = os.path.join(keys_dir, str(self._key_index)) + '_key'
        public_key = '{}.pub'.format(private_key)

        print("Using key", self._key_index, "for", role_name)
        self._key_index = self._key_index + 1

        return (
            repository_tool.import_ed25519_publickey_from_file(public_key),
            repository_tool.import_ed25519_privatekey_from_file(private_key, password='pw')
        )

    def add_target(self, filename, signing_role=None):
        repository = self.repository

        if signing_role is None:
            repository.targets.add_targets([filename])
        else:
            repository.targets(signing_role).add_targets([filename])
            repository.mark_dirty([signing_role])

        repository.mark_dirty(['snapshot', 'targets', 'timestamp'])

        return self

    def create_target(self, filename, contents=None, signing_role=None):
        if contents is None:
            contents = 'Contents: ' + filename

        path = os.path.join(self._server_dir, 'targets', filename)
        with open(path, 'w') as f:
            f.write(contents)

        self.add_target(filename, signing_role)

        return self

    def publish(self, with_client=False):
        self.repository.writeall(consistent_snapshot=True)

        staging_dir = os.path.join(self._server_dir, 'metadata.staged')
        live_dir = os.path.join(self._server_dir, 'metadata')
        shutil.copytree(staging_dir, live_dir, dirs_exist_ok=True)

        if with_client:
            repository_tool.create_tuf_client_directory(self._server_dir, self._client_dir)

        return self

    def read_signed(self, filename):
        path = os.path.join(self._server_dir, 'metadata', filename)

        with open(path, 'r') as f:
            data = json.load(f)
            return data['signed']

    def write_signed(self, filename, data, signing_role):
        path = os.path.join(self._server_dir, 'metadata', filename)

        with open(path, 'w') as f:
            data = {
                'signatures': self._sign(data, signing_role),
                'signed': data
            }
            data = json.dumps(data, indent=1, separators=(',', ': '), sort_keys=True)
            f.write(data)

    def _sign(self, data, signing_role):
        # Encode the data to canonical JSON, which is what we will actually sign.
        data = str.encode(formats.encode_canonical(data))
        # Get the private (signing) key. Currently, we assume that there's only one.
        key = self.private_keys[signing_role]
        # Sign the canonical JSON representation of the data.
        signature = signer.SSlibSigner(key).sign(data)

        return [
            signature.to_dict()
        ]

    @staticmethod
    def dir():
        return os.path.join(
            os.path.dirname(__file__),
            os.path.dirname(sys.argv[0]),
        )
