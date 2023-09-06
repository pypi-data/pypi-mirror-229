"""
Provides utilites for the package's main entrypoints.
"""

import logging
from os import environ
from typing import Iterable, List, Optional

from environ_import import __name__ as name
from environ_import.util import load_and_generate, merge_unique

__all__ = ("environ", "Optional", "List", "initialise", "add_environ")

_log = logging.getLogger(name)
_should_initialise = True


def initialise() -> None:
    """Perform all module initialisation actions."""
    # Ensure this is the first initialisation
    global _should_initialise
    if not _should_initialise:
        return
    _should_initialise = False

    # Load and generate, catching any errors
    try:
        load_and_generate()
    except Exception as e:
        _log.error("Error while initialising: %s", e)


def add_environ(globals: Iterable[str]) -> List[str]:
    """Prepends all the environment variable names to the provided globals.

    Parameters
    ----------
    globals : Iterable[str]
        The global names to prepend environment variables to.

    Returns
    -------
    List[str]
        The merged list.
    """
    return merge_unique(environ.keys(), globals)
