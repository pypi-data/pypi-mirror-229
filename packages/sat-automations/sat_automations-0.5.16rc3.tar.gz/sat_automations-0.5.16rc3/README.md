# SAT Automations

This repository contains a collection of Django apps intended to
run automation tasks that support the operations of SAT.

## Installation

```shell
# Install the package from private PyPI (CLI)
$ pip install -i https://pypi.ehps.ncsu.edu sat-automations
```

## Usage

Add the automations you want to run in your Django APPS

### Demo Automation

This is exactly what it sounds like. It is a demo automation that can be used to test the automation framework.

### Housing Automation

The housing automation is designed to run daily and process housing assignments for students.
Currently, the automation creates a CSV report of the run that can be reconciled manually with the teams external to
SAT IT. Future work will add run results to the database.

### Manage Automations

This app is currently used to manage the service accounts in the authentication process for automations.
Generally this would be the place to put models and or processes that are required to manage the automations themselves.

## Development

### Setup

Ensure you are in a virtual environment with Python 3.9.6 or higher.

```shell
> make setup
```

### Add dependencies

#### Updating Requirements

This project uses `pip-tools` to manage requirements. To update the requirements add your requirement
to the `pyproject.toml` file.

For dependencies required to run the app in production, add them to the `pyproject.toml` file under the `[project]` section.

```toml
[project]
...
dependencies = [
    "fastapi>=0.95.1, <1.0.0",
    "pyjwt>=2.6.0, <3.0.0",
    "...",
    "<YOUR NEW REQUIREMENT HERE>",
    "...",
]
```

For developer dependencies required or nice to have for development, add them to the `pyproject.toml` file under the `[project.optional-dependencies]` section.

```toml
[project.optional-dependencies]
dev = [
    "pytest>=6.2.5, <7.0.0",
    "...",
    "<YOUR NEW DEV REQUIREMENT HERE>",
    "...",
]
```

When you have add the dependency run:

```shell
$> make update-requirements
```

### Create an automation app

To create an automation app execute the following command:

NOTE: Using `test_app` for example, substitute the app name you desire.

```shell
$> python startapp.py test_app
```

This will create a new app in the `sat_automations` directory.
You will need to edit the `apps.py` file and add `sat_automations` to the name.

Example:

```python
from django.apps import AppConfig
...
class Automation(AppConfig):
    name = "sat_automations.test_app"
```

## Build and Publish

Update the version in `pyproject.toml` before building.

### Build

```shell
> flit build
```

### Publish

As long as your PyPI credentials are set up correctly, you can publish to PyPI with the following command:

```shell
> flit publish
```
