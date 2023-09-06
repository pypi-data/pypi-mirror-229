"""
The main entrypoint for the environ-import package.

Allows you to import environment variables as attributes of this module.

## Examples:
```py
from environ import PATH
print(PATH)
```
or alternatively:
```py
import environ
print(environ.PATH)
```
"""

from environ_import import internal as _internal

_internal.initialise()


def __getattr__(name: str) -> str:
    try:
        return _internal.environ[name]
    except KeyError:
        raise AttributeError(f"required environment variable '{name}' not found")


def __dir__() -> _internal.List[str]:
    return _internal.add_environ(globals().keys())
