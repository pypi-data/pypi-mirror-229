from datetime import datetime, timedelta

import dateutil.parser
import requests
from celery import shared_task
from django.conf import settings
from sat.logs import SATLogger

from sat_automations.housing_automation.config import (
    PeopleSoftProxyProvider,
)
from sat_automations.housing_automation.models import (
    AssignRevokeLog,
    AssignRevokeTracker,
    Clearance,
    ClearanceType,
    LogMessageType,
    RoomUseCode,
    StatusType,
)
from sat_automations.utils.authenticate import GoogleAuthenticate
from sat_automations.utils.managers import BulkCreateManager

logger = SATLogger(__name__)


class HousingAssignRevoke:
    def __init__(self) -> None:
        self.authenticator = GoogleAuthenticate("housing")
        self.authenticator.authenticate()
        if self.authenticator.response_json:
            self.access_token = self.authenticator.response_json.get("auth_token")
        else:
            logger.error(
                f"Unable to authenticate with auth service. Error: {self.authenticator.error_message}"
            )
            raise ConnectionError("Unable to authenticate with auth service.")
        # When this is in a test environment it will give us test data rather than nothing.
        self.people_soft_proxy = PeopleSoftProxyProvider(access_token=self.access_token)
        self.bulk_create_manager = BulkCreateManager()

    def write_logs(
        self,
        campus_id: str,
        building_code: str,
        clearance_type: ClearanceType,
        status: StatusType,
        message: LogMessageType,
        extra_info: str = None,
    ):
        assign_revoke_log = AssignRevokeLog(
            campus_id=int(campus_id),
            building_code=building_code,
            clearance_type=clearance_type,
            status=status,
            message=message,
            extra_info=extra_info,
        )
        self.bulk_create_manager.add(assign_revoke_log)

    def store_peoplesoft_records(self, management_action: ClearanceType):
        # Queries the PeopleSoft API for housing that are marked either ASSIGN or REVOKE and
        # writes them to the database, for the other steps of the automation to process.
        housing_automation_list = self.people_soft_proxy.get_housing(management_action)
        if housing_automation_list[0].get("Message"):
            logger.info("No records are being written due to:" f" {housing_automation_list[0]}")
        else:
            logger.info(f"Storing {len(housing_automation_list)} of type {management_action}.")
            self.store_actions(housing_automation_list, management_action)

    def housing_data_automation(self, management_action: ClearanceType):
        logger.debug(f"Starting {management_action} Housing Automation.")
        yesterday = (datetime.now() - timedelta(days=1)).date()
        today = datetime.now().date()
        logger.debug(f"Yesterday: {yesterday}, Today: {today}")

        # Retrieve and write the records in PeopleSoft for specified action to the Tracker.
        self.store_peoplesoft_records(management_action)
        # Next we will process the records in the Tracker.
        # Specifically, we will search for the person
        queryset = None
        if management_action == ClearanceType.REVOKE:
            logger.debug(f"Processing {management_action} actions.")
            queryset = AssignRevokeTracker.objects.filter(
                move_out_date=today,
            )
        elif management_action == ClearanceType.ASSIGN:
            logger.debug(f"Processing {management_action} actions.")
            queryset = AssignRevokeTracker.objects.filter(
                move_in_date=today,
            )
        if queryset:
            logger.info(
                f"Processing {queryset.count()} people for Clearance "
                f"Assignment Operation {management_action}."
            )
            for record in queryset:
                if self.validate_record(record):
                    self.search_and_assign_revoke_clearance(record, management_action)
        else:
            logger.info(f"No records found in the Tracker for {management_action} Clearances.")

    def validate_record(self, record: AssignRevokeTracker):
        logger.debug(f"Validating record with campus_id: {record.campus_id}")
        # If PEOPLESOFT_PROXY_URL == "TEST" then the get methods will return test data, found in
        # sat_automations/housing_automation/tests/fixtures.py
        # If PEOPLESOFT_PROXY_URL == "STAGING" then the get methods will return data from a
        # prepopulated AssignRevokeTracker.
        housing_automation_list = self.people_soft_proxy.get_person(record.campus_id)
        if len(housing_automation_list) > 0:
            if record.match_peoplesoft_list(housing_automation_list):
                return True
            else:
                logger.info(
                    f"Record with campus_id: {record.campus_id} not found. Record has been modified."
                    f" Updating this record in the Assign / Revoke Tracker to avoid processing."
                )
                record.status = StatusType.MODIFIED
                record.save()
                return False
        else:
            logger.info("Nothing to validate. No records found in peoplesoft.")
            record.status = StatusType.MODIFIED
            record.save()
            return False

    def store_actions(self, housing_list: list, management_action: ClearanceType):
        logger.debug(f"Storing {len(housing_list)} records in the Assign / Revoke Tracker.")
        for each_individual in housing_list:
            campus_id = each_individual["campus_id"]
            move_out_date = dateutil.parser.parse(each_individual["move_out_date"]).date()
            move_in_date = dateutil.parser.parse(each_individual["move_in_date"]).date()
            building_code = each_individual["room_second_description"]
            queryset = None
            if management_action == ClearanceType.REVOKE:
                queryset = AssignRevokeTracker.objects.filter(
                    campus_id=campus_id, move_out_date=move_out_date, building_code=building_code
                ).exists()
            elif management_action == ClearanceType.ASSIGN:
                queryset = AssignRevokeTracker.objects.filter(
                    campus_id=campus_id, move_in_date=move_in_date, building_code=building_code
                ).exists()

            if queryset:
                logger.info(f"{campus_id} already exists in the Assign / Revoke Tracker.")
            else:
                art = AssignRevokeTracker(
                    campus_id=campus_id,
                    move_out_date=move_out_date,
                    move_in_date=move_in_date,
                    building_code=building_code,
                )
                self.bulk_create_manager.add(art)
        self.bulk_create_manager.done()

    def apply_action_in_ccure(
        self,
        management_action: ClearanceType,
        individual: AssignRevokeTracker,
        building_room_code: str,
        clearance: Clearance,
    ):
        logger.debug(f"IN APPLY ACTION IN CCURE: {individual.campus_id}")
        try:
            clearance_name = clearance.name
            building_id = clearance.object_id

            # Assign/Revoke clearance based on the found clearance
            response = self.clearance_assign_revoke_api_request(
                management_action, individual.campus_id, building_id
            )
            if response.status_code != 200:
                individual.status = StatusType.FAIL
                logger.info(
                    f"Failed Clearance Assignment Operation [ type: {management_action} |"
                    f" campus_id: {individual.campus_id} |  building room code:"
                    f" {building_room_code} | clearance: {clearance_name}] due to:"
                    f" {response.text} ]"
                )
                self.write_logs(
                    individual.campus_id,
                    building_room_code,
                    management_action,
                    StatusType.FAIL,
                    LogMessageType.ASSIGNMENT_FAILED,
                    extra_info=response.text,
                )
            else:
                individual.status = StatusType.PASS
                logger.info(
                    "Successful Clearance Assignment Operation [ type:"
                    f" {management_action} | campus_id: {individual.campus_id} | building room"
                    f" code: {building_room_code} | clearance: {clearance_name} ]"
                )
                self.write_logs(
                    individual.campus_id,
                    building_room_code,
                    management_action,
                    StatusType.PASS,
                    LogMessageType.ASSIGNMENT_SUCCESS,
                )
        except TimeoutError as te:
            logger.info(
                f"Failed Clearance Assignment Operation [ type: {management_action} | campus_id:"
                f" {individual.campus_id} | building room code: {building_room_code}] due to Timeout:"
                f" {str(te)} ]"
            )
            self.write_logs(
                individual.campus_id,
                building_room_code,
                management_action,
                StatusType.FAIL,
                LogMessageType.ASSIGNMENT_FAILED,
                extra_info=str(te),
            )
        except Exception as e:
            logger.info(
                f"Failed Clearance Assignment Operation [ type: {management_action} | campus_id:"
                f" {individual.campus_id} | building room code: {building_room_code}] due to Exception:"
                f" {str(e)} ]"
            )
            self.write_logs(
                individual.campus_id,
                building_room_code,
                management_action,
                StatusType.FAIL,
                LogMessageType.ASSIGNMENT_FAILED,
                extra_info=str(e),
            )
        finally:
            individual.save()

    def search_and_assign_revoke_clearance(
        self, individual: AssignRevokeTracker, management_action: ClearanceType
    ):
        logger.debug(f"Searching and Assigning/Revoking clearance for {individual.campus_id}")
        building_room_code = individual.building_code
        individual_id = individual.campus_id
        try:
            clearance = RoomUseCode.objects.get(name=building_room_code).clearance
            if clearance.name == "NC":  # if there isn't a clearance associated with the room code
                individual.status = StatusType.PASS
                logger.info(
                    f"Successful Clearance Assignment Operation [ type: {management_action} | "
                    f"campus_id:{individual_id}] as {building_room_code} "
                    "doesn't have a clearance associated in the clearance MAP]"
                )
                self.write_logs(
                    individual_id,
                    building_room_code,
                    management_action,
                    StatusType.PASS,
                    LogMessageType.BUILDING_CODE_NO_CLEARANCE,
                )
            else:  # There is a clearance associated with the building code process the clearance
                logger.info("Clearance found for the building code, processing the clearance")
                self.apply_action_in_ccure(
                    management_action, individual, building_room_code, clearance
                )
        except RoomUseCode.DoesNotExist:
            individual.status = StatusType.FAIL
            logger.info(
                f"Failed Clearance Assignment Operation [type: {management_action} |"
                f" campus_id: {individual_id}] as building_code:{building_room_code} doesn't"
                " exist in the clearance MAP]"
            )
            self.write_logs(
                individual_id,
                building_room_code,
                management_action,
                StatusType.FAIL,
                LogMessageType.BUILDING_CODE_NOT_FOUND,
            )

    def clearance_assign_revoke_api_request(
        self, management_action, individual_id, clearance_id: int
    ):
        response = requests.post(
            f"{settings.CLEARANCE_SERVICE_URL}/assignments/{management_action}",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={"assignees": [str(individual_id).zfill(9)], "clearance_ids": [clearance_id]},
            timeout=600,
        )
        return response


@shared_task
def housing_assign_revoke_task():
    logger.info("RUNNING: Housing Assign Revoke.")
    har = HousingAssignRevoke()
    try:
        har.housing_data_automation(ClearanceType.ASSIGN)
        har.housing_data_automation(ClearanceType.REVOKE)
        # Ensure that any dangling records in the manager are written to the database
        har.bulk_create_manager.done()
        logger.info("COMPLETE: Housing Assign Revoke.")
    except Exception as ex:
        logger.error(f"FAILED: Housing Assign Revoke: {ex}")
