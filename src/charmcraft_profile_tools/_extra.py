import pathlib
import shutil
import subprocess

from . import _errors, _rewriter, _self, _steps

UV_ARGS = ['--quiet', '--python', '3.10']


def implement_kubernetes_extra() -> None:
    """Implement a more complete version of the K8s charm."""
    charm_dir = _self.project_root()
    if not (charm_dir / 'kubernetes').is_dir():
        raise SystemExit(_errors.NO_KUBERNETES)
    extra = charm_dir / 'kubernetes-extra'

    step = 'Copy the Kubernetes charm'
    _steps.print_step(step, 1, 5)
    if extra.exists():
        shutil.rmtree(extra)
    shutil.copytree(charm_dir / 'kubernetes', extra)
    (extra / '.coverage').unlink(missing_ok=True)
    for dir in ['.ruff_cache', '.tox', '.venv']:
        if (extra / dir).is_dir():
            shutil.rmtree(extra / dir)
    report = _steps.passed(step)

    step = 'Add functionality to the charm'
    _steps.print_step(step, 2, 5)
    add_functionality(extra, _steps.failed(step, report))
    report = _steps.passed(step, report)

    step = 'Format the charm code'
    _steps.print_step(step, 3, 5)
    try:
        subprocess.check_call(
            ['uvx', *UV_ARGS, '--with', 'tox-uv', 'tox', '-e', 'format'],
            cwd=extra,
        )
    except subprocess.CalledProcessError:
        raise SystemExit(_steps.failed(step, report))
    report = _steps.passed(step, report)

    step = 'Lint the charm code'
    _steps.print_step(step, 4, 5)
    try:
        subprocess.check_call(
            ['uvx', *UV_ARGS, '--with', 'tox-uv', 'tox', '-e', 'lint'],
            cwd=extra,
        )
    except subprocess.CalledProcessError:
        raise SystemExit(_steps.failed(step, report))
    report = _steps.passed(step, report)

    step = "Run the charm's unit tests"
    _steps.print_step(step, 5, 5)
    try:
        subprocess.check_call(
            ['uvx', *UV_ARGS, '--with', 'tox-uv', 'tox', '-e', 'unit'],
            cwd=extra,
        )
    except subprocess.CalledProcessError:
        raise SystemExit(_steps.failed(step, report))
    print(_steps.passed(step, report))


def add_functionality(extra: pathlib.Path, step_failure: str) -> None:
    # Change the container image to the demo server from the K8s charm tutorial:
    # https://documentation.ubuntu.com/ops/latest/tutorial/from-zero-to-hero-write-your-first-kubernetes-charm/study-your-application/
    r = _rewriter.Rewriter(extra / 'charmcraft.yaml')
    r.fwd(
        prefix='    upstream-source: some-repo/some-image:some-tag',
        change='    upstream-source: ghcr.io/canonical/api_demo_server:1.0.2',
    )
    r.save()

    # Change the Pebble layer so that Pebble starts the server.
    r = _rewriter.Rewriter(extra / 'src/charm.py')
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
    try:
        subprocess.check_call(['uv', 'add', *UV_ARGS, 'requests==2.33.0'], cwd=extra)
    except subprocess.CalledProcessError:
        raise SystemExit(step_failure)
    r = _rewriter.Rewriter(extra / 'src/my_application.py')
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
    r = _rewriter.Rewriter(extra / 'tests/integration/test_charm.py')
    r.fwd('import pytest', remove_line=True)
    r.fwd(
        prefix='@pytest.mark.skip',
        change='# @pytest.mark.skip',
    )
    r.fwd('    assert version', remove_line=True)
    r.add('    assert version == "1.0.2"')
    r.save()
