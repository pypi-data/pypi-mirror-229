import pytest

from sat_automations.housing_automation.models import (
    AssignRevokeLog,
    Clearance,
    ClearanceType,
    LogMessageType,
    StatusType,
)

pytestmark = pytest.mark.django_db


def test_assign_revoke_log_no_extra():
    AssignRevokeLog.objects.create(
        campus_id=123456789,
        building_code="TEST",
        clearance_type=ClearanceType.ASSIGN,
        status=StatusType.PASS,
        message=LogMessageType.ASSIGNMENT_SUCCESS,
    )
    assert AssignRevokeLog.objects.count() == 1
    assert str(AssignRevokeLog.objects.first()) == "123456789: TEST - assign - pass"


def test_assign_revoke_log_extra():
    AssignRevokeLog.objects.create(
        campus_id=123456789,
        building_code="TEST",
        clearance_type=ClearanceType.ASSIGN,
        status=StatusType.FAIL,
        message=LogMessageType.ASSIGNMENT_FAILED,
        extra_info="Network error",
    )
    assert AssignRevokeLog.objects.count() == 1
    assert AssignRevokeLog.objects.first().extra_info == "Network error"


def test_clearance():
    Clearance.objects.create(object_id=1234, name=("Fake Clearance"))
    with pytest.raises(Clearance.DoesNotExist):
        Clearance.objects.get(name="ABC")
