"""
An alternative, nullable entrypoint for the environ-import package.

Allows you to import environment variables as attributes of this module.

If the environment variable is not found `None` will be returned.

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


def __getattr__(name: str) -> _internal.Optional[str]:
    return _internal.environ.get(name)


def __dir__() -> _internal.List[str]:
    return _internal.add_environ(globals().keys())
