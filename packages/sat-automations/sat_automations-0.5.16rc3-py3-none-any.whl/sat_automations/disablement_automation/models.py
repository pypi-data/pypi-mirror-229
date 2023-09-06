from django.db import models  # noqa: F401
from model_utils.models import TimeStampedModel


class StatusType(models.TextChoices):
    PASS = "pass", "Pass"
    FAIL = "fail", "Fail"


class LogMessageType(models.TextChoices):
    DISABLEMENT_FAILED = "FC", "Failed Disablement Operation"
    DISABLEMENT_SUCCESS = "SC", "Successful Disablement Operation"


# Create your models here.


class DisablementLog(TimeStampedModel):
    """A model to track the results of the Disablement automation."""

    campus_id = models.IntegerField()
    status = models.CharField(
        choices=StatusType.choices, max_length=max(len(x) for x in StatusType.values)
    )
    message = models.CharField(
        choices=LogMessageType.choices, max_length=max(len(x) for x in LogMessageType.values)
    )
    extra_info = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Disablement Log"
        verbose_name_plural = "Disablement Logs"
        indexes = [
            models.Index(fields=["campus_id"]),
        ]

    def __str__(self):
        return f"{self.campus_id}: {self.status} - {self.message}"
