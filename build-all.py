from fixtures import (
    simple,
    rollback,
    delegated,
    threshold_two,
    threshold_two_attack
)
from unittest import mock


@mock.patch('time.time', mock.MagicMock(return_value=1577836800))
def build_all():
    simple.build()
    rollback.build()
    delegated.build()
    threshold_two.build()
    threshold_two_attack.build()


build_all()
