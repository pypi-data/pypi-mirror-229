import requests
from django.conf import settings

from sat_automations.housing_automation.models import ClearanceType, PeopleSoftProxyBase


class PeopleSoftProxy(PeopleSoftProxyBase):
    def __init__(self, access_token) -> None:
        super().__init__(access_token=access_token)
        self.base_url = settings.PEOPLESOFT_PROXY_URL

    def get_person(self, campus_id):
        housing_search_url = f"{self.base_url}/people/housing/{campus_id}"
        response = requests.get(
            housing_search_url,
            headers={"Authorization": f"Bearer {self.access_token}"},
            timeout=600,
        )
        return response.json()

    def get_housing(self, action: ClearanceType):
        housing_automation_url = f"{self.base_url}/people/housing/automation/{action}"
        response = requests.get(
            housing_automation_url,
            headers={"Authorization": f"Bearer {self.access_token}"},
            timeout=600,
        )
        return response.json()


class PeopleSoftProxyProvider:
    def __new__(cls, *args, **kwargs):
        if settings.PEOPLESOFT_PROXY_URL == "TEST":
            from sat_automations.housing_automation.tests.fixtures import PeopleSoftProxyTest

            return PeopleSoftProxyTest()
        if settings.PEOPLESOFT_PROXY_URL == "STAGING":
            from sat_automations.housing_automation.tests.fixtures import (
                PeopleSoftProxyStaging,
            )

            return PeopleSoftProxyStaging()
        return PeopleSoftProxy(*args, **kwargs)


AUTH_SERVICE_URL = settings.AUTH_SERVICE_URL
