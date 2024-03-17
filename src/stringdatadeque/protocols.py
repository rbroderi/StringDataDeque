import builtins
from collections.abc import Iterable
from collections.abc import Sequence
from typing import Annotated
from typing import Protocol
from typing import TypeGuard
from typing import TypeVar
from typing import runtime_checkable

from beartype import beartype  # pyright: ignore[reportUnknownVariableType]
from beartype.door import is_bearable  # pyright: ignore[reportUnknownVariableType]
from beartype.vale import Is  # pyright: ignore[reportUnknownVariableType]
from beartype.vale import IsInstance  # pyright: ignore[reportUnknownVariableType]


@runtime_checkable
class Printable(Protocol):  # pragma: no cover
    """Used to denote class implements custom __str__ method."""

    def __str__(self) -> str:
        """Class should implement custom str method."""
        ...


def _defines_str(obj: object) -> bool:
    return type(obj).__name__ in dir(builtins) or type(obj).__str__ != object.__str__


Builtin_or_DefinesDunderStr = Annotated[Printable, Is[_defines_str]]


# def _x_is_sequence_of_x(val: object) -> bool:
#     return isinstance(val, Sequence) and isinstance(val[0], type(val))  # pyright: ignore[reportUnknownArgumentType]


def x_is_sequence_of_x(val: object) -> bool:
    if isinstance(val, Sequence):
        return isinstance(val[0], type(val))  # pyright: ignore[reportUnknownArgumentType]
    return False


T = TypeVar("T")
# Type hint matching any non-string sequence of Convertibles.
NonRecursiveSequence = Annotated[
    Iterable[T],
    ~Is[x_is_sequence_of_x],
]
RecursiveSequence = Annotated[Sequence[T], Is[x_is_sequence_of_x]]
# Type hint matching any non-string sequence *WHOSE ITEMS ARE ALL STRINGS.*
SequenceNonstrOfStr = Annotated[Sequence[str], ~IsInstance[str]]


@beartype
def is_RecursiveSequence(val: object | Sequence[T]) -> TypeGuard[RecursiveSequence[T]]:
    return is_bearable(val, RecursiveSequence[T])


@beartype
def is_NonRecursiveSequence(
    val: object | Sequence[T],
) -> TypeGuard[NonRecursiveSequence[T]]:
    return is_bearable(val, NonRecursiveSequence[T])
