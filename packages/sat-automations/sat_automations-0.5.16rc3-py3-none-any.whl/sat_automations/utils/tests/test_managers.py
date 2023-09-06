import pytest

from sat_automations.conftest import random_assign_revoke_log
from sat_automations.housing_automation.models import AssignRevokeLog
from sat_automations.utils.managers import BulkCreateManager

pytestmark = pytest.mark.django_db


def test_bulk_create_manager():
    bcm = BulkCreateManager()
    for _ in range(99):
        bcm.add(random_assign_revoke_log())
    # At 99 objects the manager should not have created anything yet.
    assert AssignRevokeLog.objects.count() == 0
    bcm.add(random_assign_revoke_log())
    # At 100 objects the manager should have created everything.
    assert AssignRevokeLog.objects.count() == 100


def test_bulk_create_done():
    bcm = BulkCreateManager()
    for _ in range(99):
        bcm.add(random_assign_revoke_log())
    # At 99 objects the manager should not have created anything yet.
    assert AssignRevokeLog.objects.count() == 0
    bcm.done()
    # Calling done should create the remaining objects.
    assert AssignRevokeLog.objects.count() == 99
