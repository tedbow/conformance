# You should never need to run this, but this is the code that generated the
# fixed keys for fixture creation.

from tuf import repository_tool

for i in range(20):
    # The filename of the private key. The public key will have the same name,
    # suffixed with '.pub'.
    filename = '{}_key'.format(i)
    repository_tool.generate_and_write_ed25519_keypair(filename, password='pw')
