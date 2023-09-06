import csv
from datetime import datetime, timedelta
from pathlib import Path

from django.core.management.base import BaseCommand

from sat_automations.housing_automation.models import (
    AssignRevokeTracker,
    Clearance,
    ClearanceType,
    RoomUseCode,
)

tomorrow = datetime.now() + timedelta(days=1)

CLEARANCE_TYPES = [ClearanceType.ASSIGN, ClearanceType.REVOKE]


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--id-file",
            help="File containing a list of campus IDs from which to create tracker items",
        )
        parser.add_argument(
            "--clearance-name",
            help="Name of the clearance to assign to the tracker items",
        )
        parser.add_argument(
            "--object-id",
            help="Object ID of the clearance",
        )
        parser.add_argument(
            "--building-code",
            help="Building code for the tracker items",
        )

    def handle(self, *args, **options):
        # get campus IDs from file
        id_file = Path(options["id_file"])
        if not id_file.exists():
            self.stdout.write(
                self.style.WARNING(f"File {id_file} does not exist. No tracker items created.")
            )
            exit(0)
        # get or create clearance
        clearance, _ = Clearance.objects.get_or_create(
            name=options["clearance_name"],
            object_id=options["object_id"],
        )
        # get or create room use code
        room_use_code, _ = RoomUseCode.objects.get_or_create(
            name=options["building_code"],
            clearance=clearance,
        )
        # create tracker items
        self.stdout.write(self.style.SUCCESS(f"Importing campus IDs from {id_file}..."))
        with id_file.open("r") as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # skip header
            for i, row in enumerate(reader):
                if i % 2 == 0:  # roughly 50/50 split between ASSIGN and REVOKE
                    move_in_date = tomorrow
                    move_out_date = tomorrow + timedelta(days=40)
                else:
                    move_in_date = tomorrow - timedelta(days=40)
                    move_out_date = tomorrow
                if campus_id := row[26]:
                    try:
                        # There is a lot of dirty data in
                        # the Text1 field on test.
                        campus_id = int(campus_id)
                    except ValueError:
                        continue
                    AssignRevokeTracker.objects.get_or_create(
                        campus_id=campus_id,
                        move_in_date=move_in_date,
                        move_out_date=move_out_date,
                        building_code=room_use_code.name,
                    )
        self.stdout.write(self.style.SUCCESS(f"Completed import of campus IDs from {id_file}."))
