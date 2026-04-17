import os
import sys

COLOR = os.isatty(sys.stdout.fileno()) and not bool(os.getenv('NO_COLOR'))


def print_step(step: str, num: int, of: int) -> None:
    full_step = f'\nStep {num}/{of} - {step}'
    if COLOR:
        print(f'\033[1m{full_step}\033[0m')
    else:
        print(full_step)


def passed(step: str, report: str = '') -> str:
    return f'{report}\n✅ {step}'


def failed(step: str, report: str = '') -> str:
    return f'{report}\n❌ {step}'
