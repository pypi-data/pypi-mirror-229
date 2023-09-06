import pytest

from sat_automations.manage_automations.models import ServiceAccount

pytestmark = pytest.mark.django_db

DUMMY_SERVICE_ACCOUNT = {
    "type": "service_account",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "client_id": "ABCDE123456",
    "token_uri": "https://oauth2.googleapis.com/token",
    "project_id": "dummy-test-354015",
    "private_key": "-----BEGIN PRIVATE KEY-----\nDUMMY PRIVATE KEY",
    "client_email": "dummy-automation@dummy-test-354015.iam.gserviceaccount.com",
    "private_key_id": "c7e6ec34b7ebd14f4962138c25fd0c7fd7f66168",
    "universe_domain": "googleapis.com",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/dummy-automation%40dummy-test-354015.iam.gserviceaccount.com",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
}


def test_service_account_create(django_user_model):
    user_email = "test@example.com"
    django_user_model.objects.create(email=user_email, password="test")
    ServiceAccount.objects.create(
        created_by=django_user_model.objects.first().email,
        service_name="dummy",
        service_account_data=DUMMY_SERVICE_ACCOUNT,
    )
    assert ServiceAccount.objects.count() == 1
    assert str(ServiceAccount.objects.first()) == DUMMY_SERVICE_ACCOUNT.get("client_email")
    assert ServiceAccount.objects.first().client_email == DUMMY_SERVICE_ACCOUNT.get("client_email")
    assert ServiceAccount.objects.first().client_x509_cert_url == DUMMY_SERVICE_ACCOUNT.get(
        "client_x509_cert_url"
    )
