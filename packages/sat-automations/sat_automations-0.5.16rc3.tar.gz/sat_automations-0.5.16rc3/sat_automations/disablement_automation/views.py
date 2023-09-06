from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from sat_automations.disablement_automation.tasks import disablement_task


@login_required
def run_disablement_automation_task(request):
    disablement_task.delay()
    return redirect("/")
