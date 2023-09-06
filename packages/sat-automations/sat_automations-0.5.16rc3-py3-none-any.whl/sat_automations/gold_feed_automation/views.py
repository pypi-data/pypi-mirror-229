from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from sat_automations.gold_feed_automation.tasks import gold_feed_automation_task


@login_required
def run_gold_feed_automation_task(request):
    gold_feed_automation_task.delay()
    return redirect("/")
