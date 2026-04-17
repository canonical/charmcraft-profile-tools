import pathlib

from . import _errors


def project_root() -> pathlib.Path:
    package_dir = pathlib.Path(__file__).parent
    assert package_dir.name == 'charmcraft_profile_tools', (
        f'Unexpected package directory: {package_dir}'
    )
    src_dir = package_dir.parent
    if not src_dir.name == 'src':
        raise SystemExit(_errors.NOT_FROM_SOURCE)
    return src_dir.parent
