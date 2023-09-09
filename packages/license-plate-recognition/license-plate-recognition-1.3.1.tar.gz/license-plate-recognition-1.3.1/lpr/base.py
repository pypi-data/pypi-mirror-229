# base.py

import os
import subprocess
from pathlib import Path

__all__ = [
    "root",
    "source",
    "dataset",
    "tesseract",
    "run_silent_command"
]

def root() -> str:
    """
    Returns the root of the source program.

    :return: The path to the source.
    """

    try:
        if os.getcwd() in os.environ['VIRTUAL_ENV']:
            path = Path(__file__).parent

        else:
            raise KeyError
        # end if

    except KeyError:
        if os.getcwd() not in (
            path := str(Path(__file__).parent)
        ):
            path = os.getcwd()
        # end if
    # end try

    return str(path)
# end root

def source() -> str:
    """
    Returns the root of the source program.

    :return: The path to the source.
    """

    return str(Path(root()) / Path("source"))
# end source

def dataset() -> str:
    """
    Returns the root of the source program.

    :return: The path to the source.
    """

    return str(Path(source()) / Path("dataset"))
# end dataset

def tesseract() -> str:
    """
    Returns the root of the source program.

    :return: The path to the source.
    """

    return str(Path(source()) / Path("tesseract"))
# end tesseract

def run_silent_command(command: str) -> None:
    """
    Runs a command with no output.

    :param command: The command to run.
    """

    subprocess.run(list(command.split(" ")), capture_output=True)
# end run_silent_command