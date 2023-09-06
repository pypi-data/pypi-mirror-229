from datetime import datetime, timedelta

import pytest

from sat_automations.housing_automation.models import (
    AssignRevokeLog,
    AssignRevokeTracker,
    ClearanceType,
    LogMessageType,
    StatusType,
)
from sat_automations.housing_automation.tasks import HousingAssignRevoke
from sat_automations.housing_automation.tests.fixtures import (
    PEOPLESOFT_RESPONSE_EXAMPLES_ASSIGN,
)

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def use_test_peoplesoft_proxy(settings):
    settings.PEOPLESOFT_PROXY_URL = "TEST"


def test_housing_assign_revoke_store_no_records(mocker, caplog):
    mocker.patch("sat_automations.housing_automation.tasks.GoogleAuthenticate")
    mocker.patch("sat_automations.housing_automation.tasks.PeopleSoftProxyProvider")
    har = HousingAssignRevoke()
    har.people_soft_proxy.get_housing.return_value = [{"Message": "No records found"}]
    har.store_peoplesoft_records(ClearanceType.ASSIGN)
    assert "No records found" in caplog.text


def test_housing_assign_revoke_store_assign(mocker):
    mocker.patch("sat_automations.housing_automation.tasks.GoogleAuthenticate")
    har = HousingAssignRevoke()
    har.store_peoplesoft_records(ClearanceType.ASSIGN)
    assert AssignRevokeTracker.objects.all().count() == 4


def test_housing_assign_revoke_store_revoke(mocker):
    mocker.patch("sat_automations.housing_automation.tasks.GoogleAuthenticate")
    har = HousingAssignRevoke()
    har.store_peoplesoft_records(ClearanceType.REVOKE)
    assert AssignRevokeTracker.objects.all().count() == 2


def test_housing_assign_revoke_store_exists(mocker, caplog):
    mocker.patch("sat_automations.housing_automation.tasks.GoogleAuthenticate")
    har = HousingAssignRevoke()
    har.store_peoplesoft_records(ClearanceType.REVOKE)
    har.store_peoplesoft_records(ClearanceType.REVOKE)
    assert "already exists in the Assign / Revoke Tracker." in caplog.text


def test_housing_assign_revoke_date_only(mocker):
    import datetime

    mocker.patch("sat_automations.housing_automation.tasks.GoogleAuthenticate")
    har = HousingAssignRevoke()
    har.store_peoplesoft_records(ClearanceType.ASSIGN)
    assert type(AssignRevokeTracker.objects.first().move_in_date) == datetime.date
    assert type(AssignRevokeTracker.objects.first().move_out_date) == datetime.date


def test_housing_assign_revoke_today(mocker):
    mocker.patch("sat_automations.housing_automation.tasks.GoogleAuthenticate")
    yesterday = (datetime.now() - timedelta(days=1)).date()
    har = HousingAssignRevoke()
    har.store_peoplesoft_records(ClearanceType.REVOKE)
    queryset = AssignRevokeTracker.objects.filter(
        move_out_date=yesterday,
    )
    assert queryset.count() == 1


def test_housing_data_automation_no_assign(mocker, caplog):
    mocker.patch("sat_automations.housing_automation.tasks.GoogleAuthenticate")
    mocker.patch("sat_automations.housing_automation.tasks.PeopleSoftProxyProvider")
    har = HousingAssignRevoke()
    har.people_soft_proxy.get_housing.return_value = [{"Message": "No records found"}]
    har.housing_data_automation(ClearanceType.ASSIGN)
    assert f"No records found in the Tracker for {ClearanceType.ASSIGN}" in caplog.text


def test_housing_data_automation_no_matching_ps_record(mocker, caplog):
    mocker.patch("sat_automations.housing_automation.tasks.GoogleAuthenticate")
    mocker.patch("sat_automations.housing_automation.tasks.PeopleSoftProxyProvider")
    har = HousingAssignRevoke()
    har.people_soft_proxy.get_housing.return_value = [
        x for x in PEOPLESOFT_RESPONSE_EXAMPLES_ASSIGN.values()
    ]
    har.people_soft_proxy.get_person.return_value = []
    har.housing_data_automation(ClearanceType.ASSIGN)
    assert "Nothing to validate. No records found in peoplesoft." in caplog.text
    art = AssignRevokeTracker.objects.all()
    assert art.count() == 4


def test_housing_data_automation_no_revoke(mocker, caplog):
    mocker.patch("sat_automations.housing_automation.tasks.GoogleAuthenticate")
    mocker.patch("sat_automations.housing_automation.tasks.PeopleSoftProxyProvider")
    har = HousingAssignRevoke()
    har.people_soft_proxy.get_housing.return_value = [{"Message": "No records found"}]
    har.housing_data_automation(ClearanceType.REVOKE)
    assert f"No records found in the Tracker for {ClearanceType.REVOKE}" in caplog.text


def test_housing_data_automation_assign(mocker):
    mocker.patch("sat_automations.housing_automation.tasks.GoogleAuthenticate")
    har = HousingAssignRevoke()
    har.search_and_assign_revoke_clearance = mocker.MagicMock()
    har.search_and_assign_revoke_clearance.return_value = True
    har.housing_data_automation(ClearanceType.ASSIGN)
    assert har.search_and_assign_revoke_clearance.call_count == 3


def test_housing_data_automation_revoke(mocker):
    mocker.patch("sat_automations.housing_automation.tasks.GoogleAuthenticate")
    har = HousingAssignRevoke()
    har.search_and_assign_revoke_clearance = mocker.MagicMock()
    har.search_and_assign_revoke_clearance.return_value = True
    har.housing_data_automation(ClearanceType.REVOKE)
    assert har.search_and_assign_revoke_clearance.call_count == 1


def test_housing_data_automation_no_clearance(mocker, caplog):
    mocker.patch("sat_automations.housing_automation.tasks.GoogleAuthenticate")
    mocker.patch("sat_automations.housing_automation.tasks.PeopleSoftProxyProvider")
    har = HousingAssignRevoke()
    ps_response = PEOPLESOFT_RESPONSE_EXAMPLES_ASSIGN.copy()
    del ps_response["200536401"]
    del ps_response["200536403"]
    del ps_response["200536406"]
    har.people_soft_proxy.get_housing.return_value = [ps_response.get("200536407")]
    har.people_soft_proxy.get_person.return_value = [ps_response.get("200536407")]
    har.housing_data_automation(ClearanceType.ASSIGN)
    assert "doesn't have a clearance associated in the clearance MAP" in caplog.text
    har.bulk_create_manager.done()
    arl = AssignRevokeLog.objects.first()
    assert arl.message == LogMessageType.BUILDING_CODE_NO_CLEARANCE
    assert arl.status == StatusType.PASS
    assert arl.clearance_type == ClearanceType.ASSIGN


def test_housing_data_automation_no_building(mocker, caplog):
    mocker.patch("sat_automations.housing_automation.tasks.GoogleAuthenticate")
    mocker.patch("sat_automations.housing_automation.tasks.PeopleSoftProxyProvider")
    har = HousingAssignRevoke()
    del PEOPLESOFT_RESPONSE_EXAMPLES_ASSIGN["200536401"]
    del PEOPLESOFT_RESPONSE_EXAMPLES_ASSIGN["200536403"]
    del PEOPLESOFT_RESPONSE_EXAMPLES_ASSIGN["200536407"]
    har.people_soft_proxy.get_housing.return_value = [
        PEOPLESOFT_RESPONSE_EXAMPLES_ASSIGN.get("200536406")
    ]
    har.people_soft_proxy.get_person.return_value = [
        PEOPLESOFT_RESPONSE_EXAMPLES_ASSIGN.get("200536406")
    ]
    har.housing_data_automation(ClearanceType.ASSIGN)
    assert "Failed Clearance Assignment Operation" in caplog.text
    har.bulk_create_manager.done()
    arl = AssignRevokeLog.objects.first()
    assert arl.message == LogMessageType.BUILDING_CODE_NOT_FOUND
    assert arl.status == StatusType.FAIL
    assert arl.clearance_type == ClearanceType.ASSIGN


# TODO: Add tests for the apply_action_in_ccure method
