import pytest

from sat_automations.disablement_automation.models import (
    DisablementLog,
    LogMessageType,
    StatusType,
)

pytestmark = pytest.mark.django_db


def test_disablement_no_extra():
    DisablementLog.objects.create(
        campus_id=123456789,
        status=StatusType.PASS,
        message=LogMessageType.DISABLEMENT_SUCCESS,
    )
    assert DisablementLog.objects.count() == 1
    assert str(DisablementLog.objects.first()) == "123456789: pass - SC"


def test_disablement_extra():
    DisablementLog.objects.create(
        campus_id=123456789,
        status=StatusType.FAIL,
        message=LogMessageType.DISABLEMENT_FAILED,
        extra_info="Network error",
    )
    assert DisablementLog.objects.count() == 1
    assert DisablementLog.objects.first().extra_info == "Network error"
