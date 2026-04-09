import pathlib
import shutil
import subprocess

from ._rewriter import Rewriter

KUBERNETES = pathlib.Path('kubernetes')
KUBERNETES_EXTRA = pathlib.Path('kubernetes-extra')


def implement_kubernetes_extra() -> None:
    """Implement a more complete version of the K8s charm."""

    # Copy the K8s charm.
    assert KUBERNETES.is_dir()
    shutil.rmtree(KUBERNETES_EXTRA, ignore_errors=True)
    shutil.copytree(KUBERNETES, KUBERNETES_EXTRA)

    # Delete any files/dirs created when running the K8s charm's tests.
    (KUBERNETES_EXTRA / '.coverage').unlink(missing_ok=True)
    for dir in ['.ruff_cache', '.tox', '.venv']:
        shutil.rmtree(KUBERNETES_EXTRA / dir, ignore_errors=True)

    # Change the container image to the demo server from the K8s charm tutorial:
    # https://documentation.ubuntu.com/ops/latest/tutorial/from-zero-to-hero-write-your-first-kubernetes-charm/study-your-application/
    r = Rewriter(KUBERNETES_EXTRA / 'charmcraft.yaml')
    r.fwd(
        prefix='    upstream-source: some-repo/some-image:some-tag',
        change='    upstream-source: ghcr.io/canonical/api_demo_server:1.0.2',
    )
    r.save()

    # Change the Pebble layer so that Pebble starts the server.
    r = Rewriter(KUBERNETES_EXTRA / 'src/charm.py')
    r.set_indent(4)
    r.fwd('def _on_pebble_ready')
    r.fwd('    layer')
    r.add('    command = "uvicorn api_demo_server.app:app --host=0.0.0.0 --port=8000"', offset=-1)
    r.set_indent(5 * 4)
    r.fwd(
        prefix='"command": "/bin/foo"',
        change='"command": command',
    )
    r.save()

    # Implement get_version() in the workload module, by requesting the version over HTTP.
    subprocess.check_call(
        ['uv', 'add', '--quiet', 'requests==2.33.0'], cwd=KUBERNETES_EXTRA
    )  # Add package to charm venv.
    r = Rewriter(KUBERNETES_EXTRA / 'src/my_application.py')
    r.fwd('import logging')
    r.add('')
    r.add('import requests')
    r.fwd('def get_version()')
    r.fwd('    return', remove_line=True)
    r.add("""\
    response = requests.get("http://localhost:8000/version")
    resonse_data = response.json()
    return resonse_data["version"]""")
    r.save()

    # Enable the integration test that checks the workload version.
    r = Rewriter(KUBERNETES_EXTRA / 'tests/integration/test_charm.py')
    r.fwd('import pytest', remove_line=True)
    r.fwd(
        prefix='@pytest.mark.skip',
        change='# @pytest.mark.skip',
    )
    r.fwd('    assert version', remove_line=True)
    r.add('    assert version == "1.0.2"')
    r.save()

    # Format the charm code (just in case) then run the charm's tests.
    subprocess.check_call(
        ['uvx', '--with', 'tox-uv', 'tox', '-e', 'format,lint,unit'], cwd=KUBERNETES_EXTRA
    )
