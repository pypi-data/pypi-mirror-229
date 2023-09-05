from __future__ import annotations

from typing import TypeVar

from typing_extensions import Generic

_T = TypeVar("_T")


class Echo(Generic[_T]):
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value: _T) -> _T:
        """Write the value by returning it, instead of storing in a buffer."""
        return value
