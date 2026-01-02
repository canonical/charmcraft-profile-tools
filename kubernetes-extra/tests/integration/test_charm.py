# Copyright 2026 Charmer
# See LICENSE file for licensing details.
#
# The integration tests use the Jubilant library. See https://documentation.ubuntu.com/jubilant/
# To learn more about testing, see https://documentation.ubuntu.com/ops/latest/explanation/testing/

import logging
import pathlib

import jubilant
import yaml

logger = logging.getLogger(__name__)

METADATA = yaml.safe_load(pathlib.Path("charmcraft.yaml").read_text())


def test_deploy(charm: pathlib.Path, juju: jubilant.Juju):
    """Deploy the charm under test."""
    resources = {
        "some-container-image": METADATA["resources"]["some-container-image"]["upstream-source"]
    }
    juju.deploy(charm.resolve(), app="my-application", resources=resources)
    juju.wait(jubilant.all_active)


# If you implement my_application.get_version in the charm source,
# remove the @pytest.mark.skip line to enable this test.
# Alternatively, remove this test if you don't need it.
# @pytest.mark.skip(reason="my_application.get_version is not implemented")
def test_workload_version_is_set(charm: pathlib.Path, juju: jubilant.Juju):
    """Check that the correct version of the workload is running."""
    version = juju.status().apps["my-application"].version
    assert version == "1.0.0"  # (Bug) workload ought to return 1.0.1 instead.
