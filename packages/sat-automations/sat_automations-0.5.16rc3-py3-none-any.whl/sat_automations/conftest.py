import random

import pytest
from faker import Faker

from sat_automations.housing_automation.models import (
    AssignRevokeLog,
    ClearanceType,
    LogMessageType,
    StatusType,
)

Faker.seed(random.randint(0, 1000))

fake = Faker()

pytestmark = pytest.mark.django_db


def random_assign_revoke_log():
    return AssignRevokeLog(
        campus_id=fake.random_int(min=0, max=999999999),
        building_code=f"{fake.word()} {fake.word()}-{fake.random_int(min=100, max=400)}-{fake.random_letter().upper()}",
        clearance_type=ClearanceType(random.choice(ClearanceType.choices)[0]),
        status=StatusType(random.choice(StatusType.choices)[0]),
        message=LogMessageType(random.choice(LogMessageType.choices)[0]),
    )
