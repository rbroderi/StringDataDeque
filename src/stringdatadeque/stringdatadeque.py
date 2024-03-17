"""Holds StringDeque class as well as several implementations of it."""

from collections import deque
from collections.abc import Callable
from collections.abc import Sequence
from typing import Generic
from typing import Self
from typing import SupportsIndex
from typing import TypeVar
from typing import cast
from typing import overload

from beartype import beartype  # pyright: ignore[reportUnknownVariableType]
from beartype.door import is_bearable  # pyright: ignore[reportUnknownVariableType]

from .protocols import Builtin_or_DefinesDunderStr
from .protocols import SequenceNonStr
from .protocols import SequenceNonstrOfStr

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
        data: Sequence[ConvertibleToDataType] | ConvertibleToDataType | None = None,
        sep: str = "",
    ) -> None:
        """Initialize the StringDataDeque."""
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

    def __ror__(self, other: SequenceNonStr[ConvertibleToDataType]) -> Self:
        """Right or."""
        # self._data.extend(map(self.convert_func, other))
        self.insert(other)
        return self

    def __ior__(self, other: SequenceNonStr[ConvertibleToDataType]) -> Self:
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

    @overload
    def insert(
        self,
        other: SequenceNonStr[ConvertibleToDataType] | ConvertibleToDataType,
        /,
        pre_process_func: Callable[[ConvertibleToDataType], ConvertibleToDataType]
        | None = None,
        skip_conversion: bool = False,
    ) -> Self: ...

    @overload
    def insert(
        self,
        other: SequenceNonStr[DataType] | DataType,
        /,
        pre_process_func: Callable[[DataType], DataType] | None = None,
        skip_conversion: bool = True,
    ) -> Self: ...

    @overload
    def insert(
        self,
        other: SequenceNonStr[T] | T,
        /,
        pre_process_func: Callable[[T], ConvertibleToDataType] | None = None,
        skip_conversion: bool = False,
    ) -> Self: ...

    def insert(
        self,
        other: SequenceNonStr[T]
        | T
        | SequenceNonStr[ConvertibleToDataType]
        | ConvertibleToDataType
        | SequenceNonStr[DataType]
        | DataType,
        pre_process_func: Callable[[ConvertibleToDataType], ConvertibleToDataType]
        | Callable[[DataType], ConvertibleToDataType]
        | Callable[[T], ConvertibleToDataType]
        | None = None,
        skip_conversion: bool = False,
    ) -> Self:
        if pre_process_func is None and skip_conversion:
            is_bearable(other, Sequence[DataType] | DataType)
            other = cast(Sequence[DataType] | DataType, other)
            return self._insert_no_pre_or_conv(other)
        if pre_process_func is None:
            is_bearable(other, Sequence[ConvertibleToDataType] | ConvertibleToDataType)
            other = cast(Sequence[ConvertibleToDataType] | ConvertibleToDataType, other)
            return self._insert_no_pre(other)
        data = cast(Sequence[T] | T, other)
        pre_process_func = cast(Callable[[T], ConvertibleToDataType], pre_process_func)
        return self._insert(data, pre_process_func)

    def _insert(
        self,
        other: Sequence[T] | T,
        pre_process_func: Callable[[T], ConvertibleToDataType],
    ) -> Self:
        data = other
        if not isinstance(other, Sequence) or isinstance(other, str):
            data = (other,)
        data = cast(Sequence[T], data)
        data = tuple(map(pre_process_func, data))
        self._insert_no_pre(data)
        return self

    def _insert_no_pre(
        self, other: Sequence[ConvertibleToDataType] | ConvertibleToDataType
    ) -> Self:
        data = other
        if not isinstance(other, Sequence) or isinstance(other, str):
            data = (other,)
        data = cast(Sequence[ConvertibleToDataType], data)
        data = tuple(map(self.convert_func, data))
        self._insert_no_pre_or_conv(data)
        return self

    def _insert_no_pre_or_conv(self, other: Sequence[DataType] | DataType) -> Self:
        data = other
        if not isinstance(other, Sequence) or isinstance(other, str):
            data = (other,)
        data = cast(Sequence[DataType], data)
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
