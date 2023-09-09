import os
from time import sleep
from thunder.tools import get_shell_type
from pathlib import Path

SHELL_TYPE = get_shell_type()


def _clear_terminal():
    with open(os.devnull, 'w') as devnull:
        print(os.system('clear'), file=devnull)


if SHELL_TYPE != 'TERMINAL':
    from IPython.display import clear_output

    clear = clear_output
else:
    clear = _clear_terminal


def boolpicker(name, default=True) -> bool:
    question = name.rstrip('?').upper() + '?'
    while True:
        clear()
        print(question)
        sleep(0.2)
        print(f'T  ◆  True')
        print(f'F  ◆  False')
        sleep(0.2)
        try:
            choice = input(f'[T-F] : ')
            if choice == '':
                clear()
                return default
            if choice.lower() == 't':
                clear()
                return True
            if choice.lower() == 'f':
                clear()
                return False
        except ValueError:
            pass
