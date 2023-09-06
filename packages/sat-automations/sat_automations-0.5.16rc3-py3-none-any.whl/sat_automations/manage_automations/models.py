from django.db import models  # noqa: F401
from model_utils.models import TimeStampedModel
from simple_history.models import HistoricalRecords


# Create your models here.
class ServiceAccount(TimeStampedModel):
    created_by = models.EmailField(max_length=254)
    service_name = models.CharField(max_length=32, null=True, blank=False)
    service_account_data = models.JSONField()
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.service_account_data['client_email']}"

    @property
    def client_email(self):
        return self.service_account_data.get("client_email", "")

    @property
    def client_x509_cert_url(self):
        return self.service_account_data.get("client_x509_cert_url", "")
