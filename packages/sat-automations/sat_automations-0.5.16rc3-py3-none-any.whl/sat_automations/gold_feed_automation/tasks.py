from celery import shared_task
from sat.logs import SATLogger

logger = SATLogger(__name__)


@shared_task
def gold_feed_automation_task(option: str):
    logger.info("gold_feed_automation task")
    if option.lower() == "success":
        logger.info("finished gold_feed_automation task")
        return "Success"
    logger.info("failed gold_feed_automation task")
    return "Fail"
