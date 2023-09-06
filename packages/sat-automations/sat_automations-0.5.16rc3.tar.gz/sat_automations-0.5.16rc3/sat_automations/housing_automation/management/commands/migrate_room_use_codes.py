from django.core.management.base import BaseCommand

from sat_automations.housing_automation.data.clearance_map import clearance_map
from sat_automations.housing_automation.models import Clearance, RoomUseCode


class Command(BaseCommand):
    def handle(self, *args, **options):
        for room_use_code, clearance in clearance_map.items():
            try:
                if clearance:
                    clearance_obj, created = Clearance.objects.get_or_create(
                        name=clearance.get("Name"),
                        object_id=clearance.get("ObjectID"),
                    )
                else:
                    clearance_obj, created = Clearance.objects.get_or_create(
                        name="NO_CLEARANCE_ASSIGNED",
                        object_id=0,
                    )
                RoomUseCode.objects.get_or_create(name=room_use_code, clearance=clearance_obj)
            except Exception as e:
                print(f"{e}: {room_use_code}: {clearance}")
