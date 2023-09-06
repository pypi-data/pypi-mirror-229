# makemigrations.py
import sys
from pathlib import Path

from django.core.management import call_command

if app_name := sys.argv[1]:
    Path(f"sat_automations/{app_name}").mkdir(exist_ok=False)
    call_command("startapp", f"{app_name}", f"sat_automations/{app_name}")
