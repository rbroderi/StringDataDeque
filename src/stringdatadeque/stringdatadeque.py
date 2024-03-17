"""Holds StringDeque class as well as several implementations of it."""

from collections import deque
from collections.abc import Callable
from collections.abc import Sequence
from typing import Any
from typing import Generic
from typing import Self
from typing import SupportsIndex
from typing import TypeVar
from typing import cast
from typing import get_args
from typing import overload

from beartype import beartype  # pyright: ignore[reportUnknownVariableType]
from beartype.door import is_bearable  # pyright: ignore[reportUnknownVariableType]

from .protocols import Builtin_or_DefinesDunderStr
from .protocols import NonRecursiveSequence
from .protocols import SequenceNonstrOfStr
from .protocols import is_NonRecursiveSequence

T = TypeVar("T")
DataType = TypeVar("DataType")
ConvertibleToDataType = TypeVar("ConvertibleToDataType")


@beartype
class StringDataDeque(Generic[DataType, ConvertibleToDataType]):
    """A deque made to hold data that can be formatted as a string."""

    def __init__(
        self,
        convert_func: Callable[[ConvertibleToDataType], DataType],
        format_func: Callable[[DataType], str],
        data: NonRecursiveSequence[ConvertibleToDataType]
        | ConvertibleToDataType
        | None = None,
        sep: str = "",
    ) -> None:
        """Initialize the StringDataDeque."""
        # TODO is this the best way?
        self._DataType, self._ConvertibleToDataType = get_args(self.__orig_bases__[0])  # type: ignore
        self._data: deque[DataType] = deque()
        self.convert_func = convert_func
        self.format_func = format_func
        if data is not None:
            self.insert(data)
        self.sep = sep

    def __str__(self) -> str:
        """Return string joined by sep."""
        return self.sep.join(map(self.format_func, self._data))

    def __add__(self, other: ConvertibleToDataType) -> Self:
        """Add obj to the StringDataDeque."""
        # self._data.append(self.convert_func(other))
        self.insert(other)
        return self

    def __radd__(self, other: ConvertibleToDataType) -> Self:
        """Right add."""
        return self.__add__(other)

    def __iadd__(self, other: ConvertibleToDataType) -> Self:
        """Define +=."""
        return self.__add__(other)

    # do we want ror?
    # def __or__(self, other: NonRecursiveIterable[ConvertibleToDataType]) -> Self:
    #     """Extend StringDataDeque by iterable."""
    #     self._data.extend(map(self.convert_func, other))
    #     return self

    def __ror__(self, other: NonRecursiveSequence[ConvertibleToDataType]) -> Self:
        """Right or."""
        # self._data.extend(map(self.convert_func, other))
        self.insert(other)
        return self

    def __ior__(self, other: NonRecursiveSequence[ConvertibleToDataType]) -> Self:
        """Define |=."""
        return self.__ror__(other)

    def __len__(self) -> int:
        """Get length of the StringDataDeque."""
        return len(self._data)

    def __getitem__(self, key: SupportsIndex) -> DataType:
        """Get item by index."""
        return self._data[key]

    def __setitem__(self, key: SupportsIndex, value: ConvertibleToDataType) -> None:
        """Set item at index."""
        self._data[key] = self.convert_func(value)

    def _check_insert_no_convert_types(
        self, other: Any
    ) -> Sequence[DataType] | Sequence[ConvertibleToDataType]:
        if is_bearable(other, Sequence[self._DataType]) or is_bearable(
            other, Sequence[self._ConvertibleToDataType]
        ):
            return other
        msg = (
            "if func is None other must be of type: "
            "Sequence[DataType]|"
            "Sequence[ConvertibleToDataType]|"
            "DataType|"
            "ConvertibleToDataType"
            f" got {type(other)}"
        )
        raise TypeError(msg)

    @overload
    def insert(
        self,
        other: Sequence[DataType] | Sequence[ConvertibleToDataType],
        /,
        func: None = None,
    ) -> Self: ...

    @overload
    def insert(
        self,
        other: NonRecursiveSequence[DataType]
        | NonRecursiveSequence[ConvertibleToDataType],
        /,
        func: None = None,
    ) -> Self: ...

    @overload
    def insert(
        self,
        other: DataType | ConvertibleToDataType,
        /,
        func: None = None,
    ) -> Self: ...

    @overload
    def insert(
        self,
        other: Sequence[T],
        /,
        func: Callable[[T], ConvertibleToDataType],
    ) -> Self: ...

    @overload
    def insert(
        self,
        other: T,
        /,
        func: Callable[[T], ConvertibleToDataType],
    ) -> Self: ...

    def insert(
        self,
        other: NonRecursiveSequence[DataType]
        | NonRecursiveSequence[ConvertibleToDataType]
        | Sequence[DataType]
        | Sequence[ConvertibleToDataType]
        | DataType
        | ConvertibleToDataType
        | Sequence[T]
        | T,
        /,
        func: Callable[[T], ConvertibleToDataType] | None = None,
    ) -> Self:
        """Insert the other object into the StringDataDeque optionally applying func."""
        if not is_NonRecursiveSequence(other):
            other = (other,)  # type: ignore
        if func is None:
            data = self._check_insert_no_convert_types(other)
        else:
            other = cast(Sequence[T], other)
            data = list(map(func, other))
        if is_bearable(data, Sequence[ConvertibleToDataType]):
            data = cast(Sequence[ConvertibleToDataType], data)
            data = list(map(self.convert_func, data))
        else:
            data = cast(Sequence[DataType], other)
        self._data.extend(data)
        return self

    def clear(self) -> None:
        """Clear StringDeque."""
        self._data.clear()

    def draw(self, index: int = -1) -> DataType:
        """Draw element from Deque and return, defaults to last element."""
        ret = self._data[index]
        del self._data[index]
        return ret


@beartype
class StringDeque(StringDataDeque[str, Builtin_or_DefinesDunderStr]):
    """Base class for a string Deque."""

    def __init__(
        self,
        data: SequenceNonstrOfStr | str | None = None,
        sep: str = "",
    ) -> None:
        """Initialize the StringDeque."""
        if isinstance(data, str):
            data = [data]
        super().__init__(convert_func=str, format_func=str, data=data, sep=sep)


@beartype
class CircularStringDeque(StringDeque):
    """A circular StringBuffer, overwrites once maxlen reached."""

    def __init__(
        self,
        size: int,
        data: SequenceNonstrOfStr | str | None = None,
        sep: str = "",
    ) -> None:
        """Initialize the StringDeque."""
        super().__init__(data=data, sep=sep)
        self._size = size
        self._data = deque(self._data, maxlen=self._size)


@beartype
class WORMStringDeque(StringDeque):
    """Write once read many buffer."""

    def __init__(
        self, data: SequenceNonstrOfStr | str | None = None, sep: str = ""
    ) -> None:
        """Initialize the StringDeque."""
        super().__init__(data=data, sep=sep)

    def __setitem__(
        self,
        key: SupportsIndex,
        value: Builtin_or_DefinesDunderStr,
    ) -> None:
        """Set item at index."""
        msg = f"{self.__class__.__qualname__} does not implement setitem"
        raise NotImplementedError(
            msg,
        )

    def clear(self) -> None:
        """Clear StringDeque."""
        msg = f"{self.__class__.__qualname__} does not implement clear"
        raise NotImplementedError(
            msg,
        )


# def lazy_import_module(module_name: str) -> ModuleType:
#     """Lazy import module."""
#     if module_name not in sys.modules:
#         module = __import__(module_name)
#         sys.modules[module_name] = module
#     else:
#         module = sys.modules[module_name]
#     return module


# ############################
# test = CircularStringDeque(size=5, data="Circle", sep=",")
# test.insert(["test"])
# test = test + 1
# test.insert(2, lambda x: str(x + 1))
# test.insert([1, 2, "f"], lambda x: str(x))
# test = "3" + test
# test += 10
# test = [1, 2, 3] | test
# test = test | [3, 2, "1"]
# test |= ["end"]
# test[1] = "new"
# print(test)
# print(test[0])
# test2 = WORMBuffer(["a", "b", "c", "d"], sep=",")
# print(test2)


# # print(ROWMBuffer()._decrypt(msg, private_key))
