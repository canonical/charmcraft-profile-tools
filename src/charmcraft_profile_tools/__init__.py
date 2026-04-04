import pathlib
import os


def kubernetes() -> None:
    print('kubernetes')
    print(pathlib.Path.cwd())
    print(os.environ.get('TOOL_SOURCE'))


def machine() -> None:
    print('machine')
    print(pathlib.Path.cwd())
    print(os.environ.get('TOOL_SOURCE'))
