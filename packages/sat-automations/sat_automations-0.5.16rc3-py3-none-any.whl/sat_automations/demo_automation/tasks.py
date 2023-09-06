from tempfile import mkstemp

from celery import shared_task
from sat.logs import SATLogger

logger = SATLogger(__name__)


@shared_task
def simple_fake_task():
    logger.info("running simple fake task")
    _, filename = mkstemp(suffix=".txt")
    with open(filename, "w") as f:
        f.write("Please delete me")
    logger.info("finished simple fake task")
    return filename


@shared_task
def simple_task_w_params(user_id, user_name, date):
    _, filename = mkstemp(suffix=".txt")
    logger.info(f"running simple task with params: {user_id}, {user_name}")
    with open(filename, "w") as f:
        f.write(f"{date}: {user_id}, {user_name}")
    logger.info("finished simple task with params")
    return filename
