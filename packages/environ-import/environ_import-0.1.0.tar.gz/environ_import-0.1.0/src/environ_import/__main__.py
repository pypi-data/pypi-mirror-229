from __future__ import annotations

import argparse
import contextlib
import logging
from typing import Set

from environ_import import __name__ as name
from environ_import import internal
from environ_import.watchdog import (
    DatedFile,
    generate_files,
    get_dated_dotenvs,
    wait_until_change,
)

_log = logging.getLogger(name)

parser = argparse.ArgumentParser(
    prog="environ_import",
    description="Watchdog to automatically update type stubs when dotenv files are modified.",
)

parser.add_argument(
    "-o",
    "--once",
    action="store_true",
    help="run the stub generator only once and immediately exit",
)

parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="set log level to DEBUG",
)

# Parse CLI Arguments
args = parser.parse_args()

# Setup Logging
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}",
        "%Y-%m-%d %H:%M:%S",
        style="{",
    )
)

logging.basicConfig(
    level=logging.DEBUG if args.verbose else logging.INFO,
    handlers=(handler,),
)

# Disable initialisation when importing entrypoints
internal._should_initialise = False

# Initialise stubs with current keys
files: Set[DatedFile] = get_dated_dotenvs()
generate_files(files)

if args.once:
    _log.info("STUB FILES GENERATED!")
else:
    with contextlib.suppress(KeyboardInterrupt):
        _log.info("WATCHDOG WATCHING...")
        while True:
            files = wait_until_change(files)
            generate_files(files)
