# Copyright 2026 Charmer
# See LICENSE file for licensing details.

"""Functions for interacting with the workload.

The intention is that this module could be used outside the context of a charm.
"""

import logging

import requests

logger = logging.getLogger(__name__)


# Functions for interacting with the workload, for example over HTTP:


def get_version() -> str | None:
    """Get the running version of the workload."""
    # You'll need to implement this function (or remove it if not needed).
    response = requests.get("http://localhost:8000/version")
    resonse_data = response.json()
    return resonse_data["version"]
