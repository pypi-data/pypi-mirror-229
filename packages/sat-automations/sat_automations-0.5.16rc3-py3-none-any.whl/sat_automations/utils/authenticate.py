import abc
from datetime import datetime, timedelta

from django.conf import settings
from google.auth import crypt, jwt
from requests import post
from sat.logs import SATLogger

from sat_automations.manage_automations.models import ServiceAccount

SERVICE_AUTHENTICATION_URL = f"{settings.AUTH_SERVICE_URL}/service-sign-in"

logger = SATLogger(__name__)


class BaseAuthenticate(abc.ABC):
    def __init__(self) -> None:
        self.response_json = None
        self.error_message = None

    @abc.abstractmethod
    def authenticate(self):
        pass


class GoogleAuthenticate(BaseAuthenticate):
    def __init__(self, automation_name) -> None:
        super().__init__()
        self.service_account = ServiceAccount.objects.filter(service_name=automation_name).first()
        self.signed_jwt = None

    def _sign_token(self):
        # The IAT has a 1 second buffer to account for clock skew
        iat = (datetime.now() - timedelta(seconds=1)).timestamp()
        exp = (datetime.now() + timedelta(minutes=2)).timestamp()
        payload = {
            "client_email": self.service_account.client_email,
            "client_x509_cert_url": self.service_account.client_x509_cert_url,
            "iat": iat,
            "exp": exp,
        }
        signer = crypt.RSASigner.from_service_account_info(
            self.service_account.service_account_data
        )
        self.signed_jwt = jwt.encode(signer, payload)

    def authenticate(self):
        self._sign_token()
        response = post(
            SERVICE_AUTHENTICATION_URL, json={"token": self.signed_jwt.decode()}, timeout=3
        )
        logger.debug(f"Response from auth service: {response.json()}")
        if response.status_code == 200:
            self.response_json = response.json()
        else:
            self.error_message = response.json().get("message")
