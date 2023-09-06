import pytest

from sat_automations.gold_feed_automation.tasks import gold_feed_automation_task


@pytest.mark.skip(reason="This is just a base app")
def test_gold_feed_automation_task(celery_app, celery_worker):
    result = gold_feed_automation_task(option="Success").delay()
    assert result == "Success"


@pytest.mark.skip(reason="This is just a base app")
def test_gold_feed_automation_task(celery_app, celery_worker):
    result = gold_feed_automation_task(option="Fail").delay()
    assert result == "Fail"

