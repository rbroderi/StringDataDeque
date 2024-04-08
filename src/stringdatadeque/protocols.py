"""Holds Protocols and types."""

import builtins
from collections.abc import Sequence
from typing import Annotated
from typing import Protocol
from typing import TypeVar
from typing import runtime_checkable

from beartype.vale import Is  # pyright: ignore[reportUnknownVariableType]
from beartype.vale import IsInstance  # pyright: ignore[reportUnknownVariableType]


@runtime_checkable
class Printable(Protocol):  # pragma: no cover
    """Used to denote class implements custom __str__ method."""

    def __str__(self) -> str:
        """Class should implement custom str method."""
        ...


def _defines_str(obj: object) -> bool:
    """Check if an object defines a custom `__str__` method.

    :param obj: An object to check.
    :type obj: object

    :return: True if the object defines a custom `__str__` method, False otherwise.
    :rtype: bool
    """
    return type(obj).__name__ in dir(builtins) or type(obj).__str__ != object.__str__


Builtin_or_DefinesDunderStr = Annotated[Printable, Is[_defines_str]]


T = TypeVar("T")
# Type hint matching any non-string sequence *WHOSE ITEMS ARE ALL STRINGS.*
SequenceNonstrOfStr = Annotated[Sequence[str], ~IsInstance[str]]
# Type hint matching any non-string sequence
SequenceNonStr = Annotated[Sequence[T], ~IsInstance[str]]
