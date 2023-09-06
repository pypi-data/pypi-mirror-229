from datetime import datetime, timedelta

from sat_automations.housing_automation.models import (
    AssignRevokeTracker,
    ClearanceType,
    PeopleSoftProxyBase,
)

YESTERDAY = datetime.now() - timedelta(days=1)
TODAY = datetime.now()
DAY_AFTER_TOMORROW = datetime.now() + timedelta(days=2)

PEOPLESOFT_RESPONSE_EXAMPLES_ASSIGN = {
    "200536401": {
        "campus_id": "200536401",
        "strm": "2237",
        "building": "Owen",
        "room_second_description": "Owen-034",
        "move_in_date": f"{YESTERDAY}",
        "move_out_date": f"{DAY_AFTER_TOMORROW}",
        "action_dttm": "2023-06-20T09:33:57",
        "room_descriptionaddress_1": "Double",
        "address_2": "04417 Owen Hall",
        "city": "2720 Cates Avenue",
        "zipcode": "Raleigh",
        "state": "27607",
        "DESCR50": "NC",
    },
    "200536403": {
        "campus_id": "200536403",
        "strm": "2237",
        "building": "Owen",
        "room_second_description": "Owen-036",
        "move_in_date": f"{TODAY}",
        "move_out_date": f"{DAY_AFTER_TOMORROW}",
        "action_dttm": "2023-06-20T09:33:57",
        "room_descriptionaddress_1": "Double",
        "address_2": "04417 Owen Hall",
        "city": "2720 Cates Avenue",
        "zipcode": "Raleigh",
        "state": "27607",
        "DESCR50": "NC",
    },
    # No Building Found
    "200536406": {
        "campus_id": "200536406",
        "strm": "2237",
        "building": "Owen",
        "room_second_description": "ABC123",
        "move_in_date": f"{TODAY}",
        "move_out_date": f"{DAY_AFTER_TOMORROW}",
        "action_dttm": "2023-06-20T09:33:57",
        "room_descriptionaddress_1": "Double",
        "address_2": "04417 Owen Hall",
        "city": "2720 Cates Avenue",
        "zipcode": "Raleigh",
        "state": "27607",
        "DESCR50": "NC",
    },
    # Building exists but no Clearance Found
    "200536407": {
        "campus_id": "200536407",
        "strm": "2237",
        "building": "Owen",
        "room_second_description": "Grk Vlg-2M-335",
        "move_in_date": f"{TODAY}",
        "move_out_date": f"{DAY_AFTER_TOMORROW}",
        "action_dttm": "2023-06-20T09:33:57",
        "room_descriptionaddress_1": "Double",
        "address_2": "04417 Owen Hall",
        "city": "2720 Cates Avenue",
        "zipcode": "Raleigh",
        "state": "27607",
        "DESCR50": "NC",
    },
}

PEOPLESOFT_RESPONSE_EXAMPLES_REVOKE = {
    # This is an example of a person who should be revoked
    "200536402": {
        "campus_id": "200536402",
        "strm": "2237",
        "building": "Owen",
        "room_second_description": "Owen-034",
        "move_in_date": f"{DAY_AFTER_TOMORROW}",
        "move_out_date": f"{YESTERDAY}",
        "action_dttm": "2023-06-20T09:33:57",
        "room_descriptionaddress_1": "Double",
        "address_2": "04417 Owen Hall",
        "city": "2720 Cates Avenue",
        "zipcode": "Raleigh",
        "state": "27607",
        "DESCR50": "NC",
    },
    "200536404": {
        "campus_id": "200536404",
        "strm": "2237",
        "building": "Owen",
        "room_second_description": "Grk Vlg-2M-337",
        "move_in_date": f"{DAY_AFTER_TOMORROW}",
        "move_out_date": f"{TODAY}",
        "action_dttm": "2023-06-20T09:33:57",
        "room_descriptionaddress_1": "Double",
        "address_2": "04417 Owen Hall",
        "city": "2720 Cates Avenue",
        "zipcode": "Raleigh",
        "state": "27607",
        "DESCR50": "NC",
    },
}


class PeopleSoftProxyTest(PeopleSoftProxyBase):
    def get_person(self, campus_id) -> list:
        if response := PEOPLESOFT_RESPONSE_EXAMPLES_ASSIGN.get(str(campus_id), {}):
            pass
        else:
            response = PEOPLESOFT_RESPONSE_EXAMPLES_REVOKE.get(str(campus_id), {})
        return [response]

    def get_housing(self, action):
        response = []
        if action == ClearanceType.ASSIGN:
            response = [v for k, v in PEOPLESOFT_RESPONSE_EXAMPLES_ASSIGN.items()]
        elif action == ClearanceType.REVOKE:
            response = [v for k, v in PEOPLESOFT_RESPONSE_EXAMPLES_REVOKE.items()]
        return response


class PeopleSoftProxyStaging(PeopleSoftProxyBase):
    """
    On staging we want to be able to control the data in
    the assign revoke tracker table. This class will
    return a called for campus_id in the tracker table instead of
    making a call to peoplesoft.

    This also disables any daily lookups from PeopleSoft
    """

    def get_person(self, campus_id) -> list:
        record = AssignRevokeTracker.objects.filter(campus_id=campus_id).first()
        return [
            {
                "campus_id": f"{record.campus_id}",
                "room_second_description": record.building_code,
                "move_in_date": record.move_in_date.strftime("%Y-%m-%d"),
                "move_out_date": record.move_out_date.strftime("%Y-%m-%d"),
            }
        ]

    def get_housing(self, action):
        return [{"Message": "No records found"}]
