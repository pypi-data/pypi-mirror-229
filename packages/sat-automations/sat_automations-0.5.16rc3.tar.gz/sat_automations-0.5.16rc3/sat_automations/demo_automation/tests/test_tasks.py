from pathlib import Path

import pytest

from sat_automations.demo_automation.tasks import simple_fake_task, simple_task_w_params


@pytest.mark.skip(reason="This is just a demo")
def test_simple_fake_task(celery_app, celery_worker):
    result = simple_fake_task.delay()
    path = Path(result.get())
    assert path.exists()


@pytest.mark.skip(reason="This is just a demo")
def test_simple_task_w_params(celery_app, celery_worker):
    result = simple_task_w_params.delay("user1", "zeb")
    path = Path(result.get())
    assert path.exists()
    with path.open() as f:
        assert f.read() == "user1, zeb"
