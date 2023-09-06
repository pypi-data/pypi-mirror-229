import pytest

from sat_automations.disablement_automation.models import (
    DisablementLog,
    LogMessageType,
    StatusType,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def disablement_log():
    return DisablementLog.objects.create(
        campus_id=123456789,
        status=StatusType.PASS,
        message=LogMessageType.DISABLEMENT_SUCCESS,
    )
