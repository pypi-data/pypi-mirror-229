from django.urls import path

from sat_automations.demo_automation.views import run_simple_task

urlpatterns = [
    path("run-w-date/<str:date_to_run>/", run_simple_task, name="run_simple_task"),
]
