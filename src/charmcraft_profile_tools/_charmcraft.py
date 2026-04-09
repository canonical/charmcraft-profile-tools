import os
import pathlib


def init_kubernetes() -> None:
    print('kubernetes')
    print(pathlib.Path.cwd())
    print(os.environ.get('TOOL_SOURCE'))


def init_machine() -> None:
    print('machine')
    print(pathlib.Path.cwd())
    print(os.environ.get('TOOL_SOURCE'))
