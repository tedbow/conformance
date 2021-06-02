"""
Contains a class to help build fixtures programmatically.
"""

from tuf import repository_tool

import os
import shutil
import sys


class FixtureBuilder:

    def __init__(self):
        # The index of the next key pair (in the keys/ directory) to use when initializing
        # a role.
        self._key_index = 0

        # If a directory of server-side metadata already exists, remove it.
        server_dir = self._server_dir()
        if os.path.isdir(server_dir):
            shutil.rmtree(server_dir)

        # If a directory of client-side metadata already exists, remove it.
        client_dir = self._client_dir()
        if os.path.isdir(client_dir):
            shutil.rmtree(client_dir)

        my_name = os.path.basename(self.dir())
        self.repository = repository_tool.create_new_repository(server_dir, my_name)
        self.repository.status()
        self._initialize_basic_roles()

    def _initialize_basic_roles(self):
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

        path = os.path.join(self._server_dir(), 'targets', filename)
        with open(path, 'w') as f:
            f.write(contents)

        self.add_target(filename, signing_role)

        return self

    def publish(self, with_client=False):
        self.repository.writeall(consistent_snapshot=True)

        server_dir = self._server_dir()
        staging_dir = os.path.join(server_dir, 'metadata.staged')
        live_dir = os.path.join(server_dir, 'metadata')
        os.rename(staging_dir, live_dir)

        if with_client:
            repository_tool.create_tuf_client_directory(server_dir, self._client_dir())

        return self

    def _server_dir(self):
        return os.path.join(self.dir(), 'server')

    def _client_dir(self):
        return os.path.join(self.dir(), 'client')

    @staticmethod
    def dir():
        return os.path.join(
            os.path.dirname(__file__),
            os.path.dirname(sys.argv[0]),
        )
