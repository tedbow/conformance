"""
Generates a fixture to simulate a rollback attack.
"""

from builder import FixtureBuilder

import os
import shutil

# Create a simple, valid fixture with a single target file.
fixture = FixtureBuilder().create_target('testtarget.txt').publish()

# Back up the server-side metadata.
server_dir = os.path.join(fixture.dir(), 'server')
backup_dir = server_dir + '_backup'
shutil.copytree(server_dir, backup_dir, dirs_exist_ok=True)

# Add a new target, updating the server-side metadata.
fixture.create_target('testtarget2.txt').publish(with_client=True)

# Revert the server-side metadata to its previous state, simulating a rollback attack.
shutil.rmtree(server_dir + '/')
os.rename(backup_dir, server_dir)
