from django.urls import path

from sat_automations.gold_feed_automation.views import run_gold_feed_automation_task

urlpatterns = [
    path("", run_gold_feed_automation_task, name="run_gold_feed_automation_task"),
]
