import logging
import requests
import pyodbc
import cx_Oracle
import pandas as pd
from sat.logs import SATLogger
from celery import shared_task
from datetime import datetime, timedelta
from config import (
    CLEARANCE_BASE_URL,
    ORACLE_LIB_PATH,
    PEOPLESOFT_ST_CONNECT_STR,
    CCURE_SERVER,
    CCURE_DB,
    CCURE_USERNAME,
    CCURE_PASSWORD
)
from sat_automations.disablement_automation.models import (
    DisablementLog,
    LogMessageType,
    StatusType
)
from sat_automations.utils.managers import BulkCreateManager
from sat_automations.utils.authenticate import GoogleAuthenticate

logger = SATLogger(__name__)


class Disablement:

    def __init__(self) -> None:
        self.hr_connection = self.hr_db()
        self.ccure_connection = self.ccure_db()
        cx_Oracle.init_oracle_client(ORACLE_LIB_PATH)
        self.authenticator = GoogleAuthenticate("disablement")
        self.authenticator.authenticate()
        if self.authenticator.response_json:
            self.access_token = self.authenticator.response_json.get("auth_token")
        else:
            logger.error(
                f"Unable to authenticate with auth service. Error: {self.authenticator.error_message}"
            )
            raise ConnectionError("Unable to authenticate with auth service.")
        self.bulk_create_manager = BulkCreateManager()

    def write_logs(
        self,
        campus_id: str,
        status: StatusType,
        message: LogMessageType,
        extra_info: str = None,
    ):
        disable_log = DisablementLog(
            campus_id=int(campus_id),
            status=status,
            message=message,
            extra_info=extra_info,
        )
        self.bulk_create_manager.add(disable_log)

    def ccure_db(self):
        try:
            ccure_connection = pyodbc.connect(
                'DRIVER={ODBC Driver 18 for SQL Server};SERVER=' + CCURE_SERVER + ';DATABASE=' + CCURE_DB +
                ';UID=' + CCURE_USERNAME + ';PWD=' + CCURE_PASSWORD + ';TrustServerCertificate=yes;' + '')
            return ccure_connection
        except Exception as e:
            logger.error(f"Failed to connect to database due to: {e}")

    def get_ccure_records(self):
        try:
            ccure_cursor = self.ccure_connection.cursor()
            query = f"""
                SELECT
                    text1
                FROM
                    ACVScore.Access.Personnel
            """
            return ccure_cursor.execute(query).fetchall()
        except Exception as e:
            logger.error(f"Failed to fetch records due to {str(e)}")

    def hr_db(self):
        try:
            hr_connection = cx_Oracle.connect(PEOPLESOFT_ST_CONNECT_STR)
            return hr_connection
        except Exception as e:
            logger.error(f"Failed to connect to database due to: {e}")

    def ccure_data_fetch(self):
        ccure_records = self.get_ccure_records()
        if not ccure_records:
            logging.info("no records found in CCURE to process")
        else:
            ccure_list = [record[0] for record in ccure_records if record[0]]
            logger.info(f"Total number of records fetched from CCURE: {len(ccure_list)}")
            return ccure_list

    def personnel_disable_api_request(self, campus_id: str):
        response = requests.post(
            f"{CLEARANCE_BASE_URL}/personnel/disable/{campus_id}",
            headers={"Authorization": f"Bearer {self.access_token}"},
            timeout=600,
        )
        return response

    def process_disablement(self, campus_id_list: list):
        now = datetime.now()
        logger.info("Started fetching all records from HR.")
        hr_df = pd.read_sql_query(f"SELECT emplid, effdt, termination_dt FROM PS_NC_CCURE_ASSGN", self.hr_connection)
        logger.info(f"Total records fetched: {len(hr_df)}")
        hr_empld_lst = hr_df.emplid.to_list()
        record_count = 0
        disabled_count = 0
        for campus_id in campus_id_list:
            record_count = record_count + 1
            if campus_id not in hr_empld_lst:
                logger.info(f"Person with campus_id: {campus_id} does not exist in the HR database")
            else:
                person_df = hr_df[hr_df['emplid'] == campus_id]
                person_df = person_df.sort_values(by='termination_dt', ascending=True)
                if len(person_df) > 0:
                    if not pd.isnull(person_df.iloc[-1]['termination_dt']):
                        effective_dt = person_df.iloc[-1]['effdt']
                        delta_date = now - timedelta(days=60)
                        if effective_dt < delta_date:
                            disabled_count = disabled_count + 1
                            logger.info(f"Person with campus_id: {campus_id} is inactive, disabling them in CCURE.")
                            api_response = self.personnel_disable_api_request(campus_id)
                            if api_response.status_code == 200:
                                disabled_count = disabled_count + 1
                                logger.info(f"Successfully disabled campus_id: {campus_id} in ccure.")
                                self.write_logs(
                                    campus_id,
                                    StatusType.PASS,
                                    LogMessageType.DISABLEMENT_SUCCESS
                                )
                            else:
                                logger.error(f"Failed to disable campus_id: {campus_id} in ccure due "
                                             f"to response: {api_response.text}")
                                self.write_logs(
                                    campus_id,
                                    StatusType.FAIL,
                                    LogMessageType.DISABLEMENT_FAILED
                                )
                    else:
                        logger.info(f"Person with campus_id:{campus_id} still active, skipping")
        self.bulk_create_manager.done()
        logger.info(f"Number of people processed: f{record_count}")
        logger.info(f"Number of people disabled: f{disabled_count}")


@shared_task
def disablement_task():
    logger.info("RUNNING: Disablement")
    dat = Disablement()
    try:
        ccure_records = dat.ccure_data_fetch()
        dat.process_disablement(ccure_records)
        logger.info("COMPLETE: Disablement")
    except Exception as ex:
        logger.error(f"FAILED: Disablement: {ex}")
