import pytest

from sat_automations.housing_automation.models import (
    AssignRevokeLog,
    ClearanceType,
    LogMessageType,
    StatusType,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def assign_revoke_log():
    return AssignRevokeLog.objects.create(
        campus_id=123456789,
        building_code="TEST",
        clearance_type=ClearanceType.ASSIGN,
        status=StatusType.PASS,
        message=LogMessageType.ASSIGNMENT_SUCCESS,
    )
