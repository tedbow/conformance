from builder import FixtureBuilder


def build():
    fixture = FixtureBuilder('threshold_two')\
        .create_target('testtarget.txt')\
        .publish()\
        .add_key('timestamp')

    fixture._role('timestamp').threshold = 2
    fixture.repository.mark_dirty(['timestamp'])
    fixture.publish(with_client=True)
