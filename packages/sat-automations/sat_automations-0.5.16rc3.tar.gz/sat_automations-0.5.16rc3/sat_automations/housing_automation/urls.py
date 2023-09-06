from django.urls import path

from sat_automations.housing_automation.views import run_housing_automation_task

urlpatterns = [
    path("", run_housing_automation_task, name="run_housing_automation_task"),
]
