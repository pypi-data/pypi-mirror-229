import json

import pytest
from bs4 import BeautifulSoup as Soup

from sat_automations.manage_automations.models import ServiceAccount
from sat_automations.manage_automations.tests.test_models import DUMMY_SERVICE_ACCOUNT

pytestmark = pytest.mark.django_db


@pytest.fixture
def service_account(django_user_model):
    user_email = "test@example.com"
    django_user_model.objects.create(email=user_email, password="test")
    return ServiceAccount.objects.create(
        created_by=django_user_model.objects.first().email,
        service_name="dummy",
        service_account_data=DUMMY_SERVICE_ACCOUNT,
    )


def test_service_account_list(admin_client, service_account):
    url = "/admin/manage_automations/serviceaccount/"
    response = admin_client.get(url)
    assert response.status_code == 200
    soup = Soup(response.content, "html.parser")
    assert soup.find("th", class_="field-service_name").text == service_account.service_name


def test_unauthorized_view(client, django_user_model):
    url = "/admin/manage_automations/"
    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(
        username=username, password=password, is_staff=True
    )
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 404


def test_authorized_view(admin_client):
    url = "/admin/manage_automations/"
    response = admin_client.get(url)
    assert response.status_code == 200
    soup = Soup(response.content, "html.parser")
    assert soup.find("tr", class_="model-serviceaccount")


def test_create_service_account(admin_client, django_user_model):
    url = "/admin/manage_automations/serviceaccount/add/"
    response = admin_client.post(
        url,
        data={"service_name": "test", "service_account_data": json.dumps(DUMMY_SERVICE_ACCOUNT)},
    )
    assert response.status_code == 302
    assert ServiceAccount.objects.count() == 1
    # When a service account is created, the created_by field is set to the email address of the user who created it.
    assert ServiceAccount.objects.first().created_by == django_user_model.objects.first().email
