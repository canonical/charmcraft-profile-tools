#!/usr/bin/env python3
# Copyright 2026 Charmer
# See LICENSE file for licensing details.

"""Charm the application."""

import logging

import ops

# A standalone module for workload-specific logic (no charming concerns):
import my_application

logger = logging.getLogger(__name__)


class MyApplicationCharm(ops.CharmBase):
    """Charm the application."""

    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        framework.observe(self.on.install, self._on_install)
        framework.observe(self.on.start, self._on_start)

    def _on_install(self, event: ops.InstallEvent):
        """Install the workload on the machine."""
        my_application.install()

    def _on_start(self, event: ops.StartEvent):
        """Handle start event."""
        self.unit.status = ops.MaintenanceStatus("starting workload")
        my_application.start()
        version = my_application.get_version()
        if version is not None:
            self.unit.set_workload_version(version)
        self.unit.status = ops.ActiveStatus()


if __name__ == "__main__":  # pragma: nocover
    ops.main(MyApplicationCharm)
