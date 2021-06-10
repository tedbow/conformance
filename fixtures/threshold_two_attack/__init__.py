from builder import FixtureBuilder


def build():
    fixture = FixtureBuilder('threshold_two_attack')\
        .add_key('timestamp')

    fixture._role('timestamp').threshold = 2
    fixture.repository.mark_dirty(['timestamp'])
    fixture.publish(with_client=True)

    fixture.repository.mark_dirty(['timestamp'])
    fixture.publish(with_client=True)
    fixture.repository.mark_dirty(['timestamp'])
    fixture.publish()

    data = fixture.read('timestamp.json')
    signature = data['signatures'][0].copy()
    data['signatures'] = [signature, signature]
    fixture.write('timestamp.json', data)
