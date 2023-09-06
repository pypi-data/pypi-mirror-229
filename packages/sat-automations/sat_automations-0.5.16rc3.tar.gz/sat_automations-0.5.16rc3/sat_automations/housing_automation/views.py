from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from sat_automations.housing_automation.tasks import housing_assign_revoke_task


@login_required
def run_housing_automation_task(request):
    housing_assign_revoke_task.delay()
    return redirect("/")
