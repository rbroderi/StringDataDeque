"""Holds StringDeque class as well as several implementations of it."""

import sys
from collections import deque
from collections.abc import Callable
from typing import Any
from typing import Generic

try:
    from typing import Self
except ImportError:  # pragma: no cover
    from typing_extensions import Self  # pragma: no cover
from collections.abc import Sequence
from typing import SupportsIndex
from typing import TypeVar
from typing import cast
from typing import overload

from beartype import BeartypeConf  # pyright: ignore[reportUnknownVariableType]
from beartype import BeartypeStrategy  # pyright: ignore[reportUnknownVariableType]
from beartype import beartype  # pyright: ignore[reportUnknownVariableType]

from .protocols import Builtin_or_DefinesDunderStr
from .protocols import SequenceNonStr

T = TypeVar("T")
DataType = TypeVar("DataType")
ConvertibleToDataType = TypeVar("ConvertibleToDataType")
# for current func name, specify 0 or no argument.
# for name of caller of current func, specify 1.
# for name of caller of caller of current func, specify 2. etc.
current_func_name = lambda n=0: sys._getframe(n + 1).f_code.co_name  # pyright: ignore[reportPrivateUsage]  # noqa: E731, SLF001
nobeartype: Any = beartype(conf=BeartypeConf(strategy=BeartypeStrategy.O0))  # pyright: ignore[reportUnknownVariableType]

# import re

# class REqual(str):
#     "Override str.__eq__ to match a regex pattern."
#     def __eq__(self, pattern):
#         return re.fullmatch(pattern, self)


class LikeMatch(str):
    """Classed used to modify match case."""

    __slots__ = ()

    # override str.__eq__ to match if pattern in string
    def __eq__(self, pattern: object) -> bool:
        """Override eq method to perform a 'like' match.

        :param pattern: Pattern string to match against.
        :return: True if pattern matches.
        """
        pattern = cast(str, pattern)
        return pattern in self


# NOTE skip type checking on _add and _or for speed
@beartype
class StringDataDeque(Generic[DataType, ConvertibleToDataType]):
    """A deque made to hold data that can be formatted as a string."""

    @overload
    def __init__(
        self,
        convert_func: Callable[[ConvertibleToDataType], DataType],
        format_func: Callable[[DataType], str],
        data: SequenceNonStr[ConvertibleToDataType] | None = None,
        sep: str = "",
    ) -> None: ...

    @overload
    def __init__(
        self,
        convert_func: Callable[[ConvertibleToDataType], DataType],
        format_func: Callable[[DataType], str],
        data: ConvertibleToDataType | None = None,
        sep: str = "",
    ) -> None: ...

    def __init__(
        self,
        convert_func: Callable[[ConvertibleToDataType], DataType],
        format_func: Callable[[DataType], str],
        data: SequenceNonStr[ConvertibleToDataType]
        | ConvertibleToDataType
        | None = None,
        sep: str = "",
    ) -> None:
        """Initialize the StringDataDeque."""
        self._data: deque[DataType] = deque()
        self.convert_func = convert_func
        self.format_func = format_func
        if data is not None:
            if isinstance(data, str) or not isinstance(data, Sequence):
                self._data.append(self.convert_func(cast(ConvertibleToDataType, data)))
            else:
                data_mapped = map(
                    self.convert_func,
                    cast(Sequence[ConvertibleToDataType], data),
                )
                self._data.extend(data_mapped)
        self.sep = sep

    @nobeartype
    def __str__(self) -> str:
        """Return string joined by sep."""
        return self.sep.join(map(self.format_func, self._data))

    def __format__(self, format_spec: str) -> str:
        """Format string with sep override."""
        match LikeMatch(format_spec):
            case "sep=":
                old_sep, self.sep = (
                    self.sep,
                    format_spec.partition("sep=")[2].strip("'\""),
                )
                ret = str(self)
                self.sep = old_sep
                return ret
            case _:
                return str(self).__format__(format_spec)

    def __contains__(self, key: DataType) -> bool:
        """Return true if key is in the StringDataDeque or the string representation."""
        return True if (key in self._data) else (self.format_func(key) in str(self))

    @nobeartype
    def __add__(self, other: ConvertibleToDataType) -> Self:
        """Add obj to the StringDataDeque."""
        self._data.append(self.convert_func(other))
        return self

    @nobeartype
    def __radd__(self, other: ConvertibleToDataType) -> Self:
        """Right add."""
        self._data.append(self.convert_func(other))
        return self

    @nobeartype
    def __iadd__(self, other: ConvertibleToDataType) -> Self:
        """Define +=."""
        self._data.append(self.convert_func(other))
        return self

    # do we want ror?
    # def __or__(self, other: NonRecursiveIterable[ConvertibleToDataType]) -> Self:
    #     """Extend StringDataDeque by iterable."""
    #     self._data.extend(map(self.convert_func, other))
    #     return self

    @nobeartype
    def __ror__(self, other: SequenceNonStr[ConvertibleToDataType]) -> Self:
        """Right or."""
        data_mapped = map(self.convert_func, other)
        self._data.extend(data_mapped)
        return self

    @nobeartype
    def __ior__(self, other: SequenceNonStr[ConvertibleToDataType]) -> Self:
        """Define ``|=`` ."""
        data_mapped = map(self.convert_func, other)
        self._data.extend(data_mapped)
        return self

    @nobeartype
    def __len__(self) -> int:
        """Get length of the StringDataDeque."""
        return len(self._data)

    @nobeartype
    def __getitem__(self, key: SupportsIndex) -> DataType:
        """Get item by index."""
        return self._data[key]

    @nobeartype
    def __setitem__(self, key: SupportsIndex, value: ConvertibleToDataType) -> None:
        """Set item at index."""
        self._data[key] = self.convert_func(value)

    @overload
    def insert(
        self,
        other: Sequence[T],
        /,
        pre_process_func: Callable[[T], ConvertibleToDataType] | None = None,
        skip_conversion: bool = False,
    ) -> Self: ...

    @overload
    def insert(
        self,
        other: T,
        /,
        pre_process_func: Callable[[T], ConvertibleToDataType] | None = None,
        skip_conversion: bool = False,
    ) -> Self: ...

    def insert(
        self,
        other: SequenceNonStr[T] | T,
        /,
        pre_process_func: Callable[[T], ConvertibleToDataType] | None = None,
        skip_conversion: bool = False,
    ) -> Self:
        """Insert item(s) into the stringDequeue.

        :param other: Item(s) to insert.
        :param pre_process_func: Function that will preprocess the data,
            defaults to None
        :param skip_conversion: Flag to skip conversion of items., defaults to False
        :return: The StringDeque.
        """
        data: Sequence[object] | object = other
        if isinstance(data, str) or not isinstance(data, Sequence):
            data = (other,)
        if pre_process_func is None:
            if skip_conversion:
                # if conversion is skipped then data must be of datatype
                self._data.extend(cast(Sequence[DataType], data))
            else:
                # if not preprocessing data must be of type convertabletodatatype
                data_mapped: map[Any] = map(
                    self.convert_func,
                    cast(Sequence[ConvertibleToDataType], data),
                )
                self._data.extend(data_mapped)
        else:
            data_mapped = map(pre_process_func, cast(Sequence[T], data))
            data_mapped = map(self.convert_func, data_mapped)
            self._data.extend(data_mapped)
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

    @overload
    def __init__(
        self,
        data: SequenceNonStr[Builtin_or_DefinesDunderStr] | None = None,
        sep: str = "",
    ) -> None: ...

    @overload
    def __init__(
        self,
        data: Builtin_or_DefinesDunderStr | None = None,
        sep: str = "",
    ) -> None: ...

    def __init__(
        self,
        data: SequenceNonStr[Builtin_or_DefinesDunderStr]
        | Builtin_or_DefinesDunderStr
        | None = None,
        sep: str = "",
    ) -> None:
        """Initialize the StringDeque."""
        super().__init__(convert_func=str, format_func=str, data=data, sep=sep)


@beartype
class CircularStringDeque(StringDeque):
    """A circular StringBuffer, overwrites once maxlen reached."""

    @overload
    def __init__(
        self,
        size: int,
        data: SequenceNonStr[Builtin_or_DefinesDunderStr] | None = None,
        sep: str = "",
    ) -> None: ...

    @overload
    def __init__(
        self,
        size: int,
        data: Builtin_or_DefinesDunderStr | None = None,
        sep: str = "",
    ) -> None: ...

    def __init__(
        self,
        size: int,
        data: SequenceNonStr[Builtin_or_DefinesDunderStr]
        | Builtin_or_DefinesDunderStr
        | None = None,
        sep: str = "",
    ) -> None:
        """Initialize the StringDeque."""
        super().__init__(data=data, sep=sep)
        self._size = size
        self._data = deque(self._data, maxlen=self._size)


@beartype
class WORMStringDeque(StringDeque):
    """Write once read many buffer."""

    @overload
    def __init__(
        self,
        data: SequenceNonStr[Builtin_or_DefinesDunderStr] | None = None,
        sep: str = "",
    ) -> None: ...

    @overload
    def __init__(
        self,
        data: Builtin_or_DefinesDunderStr | None = None,
        sep: str = "",
    ) -> None: ...

    def __init__(
        self,
        data: SequenceNonStr[Builtin_or_DefinesDunderStr]
        | Builtin_or_DefinesDunderStr
        | None = None,
        sep: str = "",
    ) -> None:
        """Initialize the WORMStringDeque."""
        super().__init__(data=data, sep=sep)

    def __setitem__(
        self,
        key: SupportsIndex,
        value: Builtin_or_DefinesDunderStr,
    ) -> None:
        """Set item at index."""
        msg = f"{self.__class__.__qualname__} does not implement {current_func_name()}"
        raise NotImplementedError(
            msg,
        )

    def clear(self) -> None:
        """Clear not implemented."""
        msg = f"{self.__class__.__qualname__} does not implement {current_func_name()}"
        raise NotImplementedError(
            msg,
        )

    def __delitem__(self, key: SupportsIndex) -> None:
        """Delete item from StringDeque.

        :param key: Item to remove
        :raises NotImplementedError: Not Enabled on WORMStringDeque.
        """
        msg = f"{self.__class__.__qualname__} does not implement {current_func_name()}"
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
