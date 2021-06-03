from builder import FixtureBuilder

FixtureBuilder('delegated')\
    .create_target('testtarget.txt')\
    .publish()\
    .delegate('unclaimed', ['level_1_*.txt'])\
    .create_target('level_1_target.txt', signing_role='unclaimed')\
    .publish(with_client=True)\
    .add_key('targets')\
    .add_key('snapshot')\
    .invalidate()\
    .publish()\
    .revoke_key('targets')\
    .revoke_key('snapshot')\
    .invalidate()\
    .publish()
