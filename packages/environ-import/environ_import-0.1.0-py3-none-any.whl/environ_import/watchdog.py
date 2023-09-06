import logging
import os
import time
from typing import Iterable, Set

from environ_import import __name__ as name
from environ_import.util import find_dotenvs, generate_stubs, parse_dotenvs

POLL_DELAY = 0.1

__all__ = ("DatedFile", "get_dated_dotenvs", "wait_until_change", "generate_files")

_log = logging.getLogger(name)


class DatedFile:
    """Represents a file and the date it was last modified."""

    def __init__(self, path: str) -> None:
        """Represents a file and the date it was last modified.

        Parameters
        ----------
        path : str
            The path to the file.
        """
        self.mtime: float = os.stat(path).st_mtime
        self.path: str = path

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, DatedFile)
            and self.path == other.path
            and self.mtime == other.mtime
        )

    def __hash__(self) -> int:
        return hash(self.path) + hash(self.mtime)


def get_dated_dotenvs() -> Set[DatedFile]:
    """Get the `DatedFile` representation of all dotenv files that should be typed.

    Returns
    -------
    Set[DatedFile]
        A set of `DatedFile` representing all dotenv files that should be typed.
    """
    return {DatedFile(p) for p in find_dotenvs(True, True)}


def wait_until_change(current: Set[DatedFile]) -> Set[DatedFile]:
    """Blocks until there is a change in the loaded dotenv files.

    Parameters
    ----------
    current : Set[DatedFile]
        The current set of `DatedFile` representing the loaded dotenvs.

    Returns
    -------
    Set[DatedFile]
        The new set of `DatedFile` reqpresnted the new loaded dotenvs.
    """
    while True:
        new = get_dated_dotenvs()
        differences = new.symmetric_difference(current)

        if len(differences) > 0:
            # Log files that changed
            for path in set(f.path for f in differences):
                _log.info("CHANGE AT: %s", path)

            # Return new dated files
            return new

        time.sleep(POLL_DELAY)


def generate_files(files: Iterable[DatedFile]):
    """Generate stubs for the dotenvs at the provided `DatedFile`s.

    Parameters
    ----------
    files : Iterable[DatedFile]
        The `DatedFile`s to generate stubs from.
    """
    generate_stubs(parse_dotenvs((f.path for f in files)))
