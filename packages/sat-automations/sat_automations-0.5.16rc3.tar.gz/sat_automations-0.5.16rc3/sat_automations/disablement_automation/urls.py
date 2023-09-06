from django.urls import path

from sat_automations.disablement_automation.views import run_disablement_automation_task

urlpatterns = [
    path("", run_disablement_automation_task, name="run_disablement_automation_task"),
]
