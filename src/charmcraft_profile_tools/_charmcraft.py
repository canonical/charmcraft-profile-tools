import os
import pathlib
import subprocess
import shutil
import sys
import tomllib

from . import _errors, _self, _steps

UV_ARGS = ['--quiet', '--python', '3.10']


def init_kubernetes() -> None:
    init_charm('kubernetes')


def init_machine() -> None:
    init_charm('machine')


def init_charm(profile: str) -> None:
    charm_dir = _self.project_root() / profile
    charmcraft_dir = charmcraft_root()

    step = 'Initialize a charm'
    _steps.print_step(step, 1, 5)
    if charm_dir.exists():
        shutil.rmtree(charm_dir)
    try:
        subprocess.check_call(
            [
                'uv',
                'run',
                *UV_ARGS,
                '--no-dev',
                'charmcraft',
                'init',
                '--project-dir',
                charm_dir,
                '--profile',
                profile,
                '--name',
                'my-application',
                '--author',
                'Charmer',
            ],
            cwd=charmcraft_dir,
        )
    except subprocess.CalledProcessError:
        raise SystemExit(_steps.failed(step))
    report = _steps.passed(step)

    step = "Lock the charm's dependencies"
    _steps.print_step(step, 2, 5)
    uv_lock_opts = sys.argv[1:]
    try:
        subprocess.check_call(['uv', 'lock', *UV_ARGS, *uv_lock_opts], cwd=charm_dir)
    except subprocess.CalledProcessError:
        raise SystemExit(_steps.failed(step, report))
    report = _steps.passed(step, report)

    step = 'Update uv.lock.j2 in Charmcraft'
    _steps.print_step(step, 3, 5)
    uv_lock = (charm_dir / 'uv.lock').read_text()
    uv_lock_template_file = charmcraft_dir / f'charmcraft/templates/init-{profile}/uv.lock.j2'
    uv_lock_template_file.write_text(uv_lock.replace('my-application', '{{ name }}'))
    report = _steps.passed(step, report)

    step = 'Lint the charm code'
    _steps.print_step(step, 4, 5)
    try:
        subprocess.check_call(
            ['uvx', *UV_ARGS, '--with', 'tox-uv', 'tox', '-e', 'lint'],
            cwd=charm_dir,
        )
    except subprocess.CalledProcessError:
        raise SystemExit(_steps.failed(step, report))
    report = _steps.passed(step, report)

    step = "Run the charm's unit tests"
    _steps.print_step(step, 5, 5)
    try:
        subprocess.check_call(
            ['uvx', *UV_ARGS, '--with', 'tox-uv', 'tox', '-e', 'unit'],
            cwd=charm_dir,
        )
    except subprocess.CalledProcessError:
        raise SystemExit(_steps.failed(step, report))
    print(_steps.passed(step, report))


def charmcraft_root() -> pathlib.Path:
    if 'CHARMCRAFT_DIR' in os.environ:
        dir = pathlib.Path(os.environ['CHARMCRAFT_DIR'])
        if has_charmcraft_pyproject(dir):
            return dir
        raise SystemExit(f'Error: No Charmcraft source located at {dir}')
    else:
        dir = _self.project_root()
        while dir != dir.parent:
            if has_charmcraft_pyproject(dir):
                return dir
            dir = dir.parent
        raise SystemExit(_errors.NOT_INSIDE_CHARMCRAFT)


def has_charmcraft_pyproject(dir: pathlib.Path) -> bool:
    pyproject_file = dir / 'pyproject.toml'
    if pyproject_file.is_file():
        pyproject = tomllib.loads(pyproject_file.read_text())
        if pyproject['project']['name'] == 'charmcraft':
            return True
    return False
