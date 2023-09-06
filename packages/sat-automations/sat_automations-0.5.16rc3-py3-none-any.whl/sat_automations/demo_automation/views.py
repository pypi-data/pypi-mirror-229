from django.apps import apps
from django.conf import settings
from django.shortcuts import redirect

from sat_automations.demo_automation.tasks import simple_task_w_params


def run_simple_task(request, date_to_run: str):
    user = apps.get_model(settings.AUTH_USER_MODEL).objects.filter(pk=request.user.pk).first()
    simple_task_w_params.delay(user.pk, user.email, date_to_run)
    return redirect("/")
