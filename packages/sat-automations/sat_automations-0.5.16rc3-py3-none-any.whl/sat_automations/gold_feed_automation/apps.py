from logging import DEBUG

import celery
from django.apps import AppConfig
from django.conf import settings
from sat.logs import SATLogger

if settings.DEBUG:
    logger = SATLogger(__name__, level=DEBUG)
else:
    logger = SATLogger(__name__)


class Automation(AppConfig):
    name = "sat_automations.gold_feed_automation"

    def ready(self):
        logger.debug(f"{celery.__name__} ready")
        logger.debug(f"{settings.CELERY_BROKER_URL}")
