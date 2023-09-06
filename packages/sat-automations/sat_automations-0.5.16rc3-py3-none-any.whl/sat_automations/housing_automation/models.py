from dateutil.parser import parse
from django.db import models  # noqa: F401
from model_utils.models import TimeStampedModel
from simple_history.models import HistoricalRecords


class ClearanceType(models.TextChoices):
    ASSIGN = "assign", "Assign"
    REVOKE = "revoke", "Revoke"


class StatusType(models.TextChoices):
    PASS = "pass", "Pass"
    FAIL = "fail", "Fail"
    MODIFIED = "modified", "Modified"


class LogMessageType(models.TextChoices):
    BUILDING_CODE_NOT_FOUND = "BC_NF", "Building code not found"
    BUILDING_CODE_NO_CLEARANCE = "BC_NC", "Building code has no clearance"
    ASSIGNMENT_FAILED = "FC", "Failed Clearance Assignment Operation"
    ASSIGNMENT_SUCCESS = "SC", "Successful Clearance Assignment Operation"


# Create your models here.


# Non-Django classes
class PeopleSoftProxyBase:
    def __init__(self, access_token=None) -> None:
        self.base_url = ""
        self.access_token = access_token

    def get_person(self, campus_id):
        pass

    def get_housing(self, action: ClearanceType):
        pass


class AssignRevokeLog(TimeStampedModel):
    """A model to track the results of the HousingAssignRevoke automation."""

    campus_id = models.IntegerField()
    building_code = models.CharField(max_length=64)
    clearance_type = models.CharField(
        choices=ClearanceType.choices, max_length=max(len(x) for x in ClearanceType.values)
    )
    status = models.CharField(
        choices=StatusType.choices, max_length=max(len(x) for x in StatusType.values)
    )
    message = models.CharField(
        choices=LogMessageType.choices, max_length=max(len(x) for x in LogMessageType.values)
    )
    extra_info = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Assign/Revoke Log"
        verbose_name_plural = "Assign/Revoke Logs"
        indexes = [
            models.Index(fields=["campus_id", "building_code"]),
        ]

    def __str__(self):
        return f"{self.campus_id}: {self.building_code} - {self.clearance_type} - {self.status}"


class AssignRevokeTracker(TimeStampedModel):
    campus_id = models.IntegerField()
    move_in_date = models.DateField()
    move_out_date = models.DateField()
    building_code = models.CharField(max_length=64)
    status = models.CharField(
        choices=StatusType.choices, max_length=max(len(x) for x in StatusType.values), null=True
    )

    class Meta:
        verbose_name = "Assign/Revoke Tracker"
        verbose_name_plural = "Assign/Revoke Tracker"
        indexes = [
            models.Index(fields=["campus_id", "building_code"]),
        ]

    def __str__(self):
        return f"{self.campus_id}: {self.status}"

    def match_peoplesoft_list(self, ps_list) -> bool:
        match = (
            str(self.campus_id),
            self.building_code,
            str(self.move_in_date),
            str(self.move_out_date),
        )
        for ps in ps_list:
            against = (
                ps.get("campus_id"),
                ps.get("room_second_description"),
                f'{parse(ps.get("move_in_date")).date()}',
                f'{parse(ps.get("move_out_date")).date()}',
            )
            if match == against:
                return True
        return False


class Clearance(TimeStampedModel):
    name = models.CharField(max_length=128)
    object_id = models.IntegerField()
    history = HistoricalRecords()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Clearance"
        verbose_name_plural = "Clearances"
        unique_together = ("object_id", "name")
        indexes = [
            models.Index(fields=["object_id", "name"]),
        ]


class RoomUseCode(TimeStampedModel):
    name = models.CharField(max_length=128)
    clearance = models.ForeignKey(Clearance, on_delete=models.PROTECT, related_name="building_code")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Room Use Code"
        verbose_name_plural = "Room Use Codes"
