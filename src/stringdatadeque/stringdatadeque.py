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


class InMatch(str):
    """A class representing a custom string type used for 'like' matching.

    :param pattern: Pattern string to match against.
    :type pattern: str
    :return: True if pattern matches.
    """

    __slots__ = ()

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
    """A generic class representing a deque of data that can be formatted as a string.

    :param convert_func: A function to convert data to a specific data type.
    :type convert_func: Callable[[ConvertibleToDataType], DataType]
    :param format_func: A function to format data as a string.
    :type format_func: Callable[[DataType], str]
    :param data: The data to be stored in the deque.
    :type data: SequenceNonStr[ConvertibleToDataType] | ConvertibleToDataType | None
    :param sep: The separator to join elements when converting to a string.
        defaults to ''
    :type sep: str
    """

    __slots__ = ("_data", "convert_func", "format_func", "sep")

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
        """Initialize the StringDataDeque.

        :param convert_func: A callable function that converts input data to a specific
            data type.
        :type convert_func: Callable[[ConvertibleToDataType], DataType]

        :param format_func: A callable function that formats the data for display.
        :type format_func: Callable[[DataType], str]

        :param data: Initial data to be processed. It can be a single element, a
            sequence of elements, or None.
        :type data: Union[ConvertibleToDataType,
            SequenceNonStr[ConvertibleToDataType], None]

        :param sep: A separator to be used when displaying the data.
        :type sep: str

        :return: None
        :rtype: None
        """
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
        """Return string joined by sep.

        :return: A string representation of the object.
        :rtype: str
        """
        return self.sep.join(map(self.format_func, self._data))

    def __format__(self, format_spec: str) -> str:
        """Format string with sep override.

        :param format_spec: A string specifying the format.
        :type format_spec: str

        :return: The formatted string.
        :rtype: str
        """
        match InMatch(format_spec):
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
        """Return true if key is in the StringDataDeque or the string representation.

        :param key: The key to check for in the data structure.
        :type key: DataType

        :return: True if the key is found in the data structure, False otherwise.
        :rtype: bool
        """
        return True if (key in self._data) else (self.format_func(key) in str(self))

    @nobeartype
    def __add__(self, other: ConvertibleToDataType) -> Self:
        """Add the input data to the StringDataDeque.

        :param other: Data to be added to the current object.
        :type other: ConvertibleToDataType

        :return: Current object after adding the input data.
        :rtype: Self
        """
        self._data.append(self.convert_func(other))
        return self

    @nobeartype
    def __radd__(self, other: ConvertibleToDataType) -> Self:
        """Right add another value to the data container.

        :param other: A value that can be converted to the underlying data
            type of the container.
        :type other: ConvertibleToDataType

        :return: The modified container with the additional value added.
        :rtype: Self
        """
        self._data.append(self.convert_func(other))
        return self

    @nobeartype
    def __iadd__(self, other: ConvertibleToDataType) -> Self:
        # """Define +=."""
        """Add another element to the data container in place.

        :param other: Another element to add to the data container.
        :type other: ConvertibleToDataType

        :return: The updated data container with the new element added.
        :rtype: Self
        """
        self._data.append(self.convert_func(other))
        return self

    # do we want ror?
    # def __or__(self, other: NonRecursiveIterable[ConvertibleToDataType]) -> Self:
    #     #"""Extend StringDataDeque by iterable."""
    #     self._data.extend(map(self.convert_func, other))
    #     return self

    @nobeartype
    def __ror__(self, other: SequenceNonStr[ConvertibleToDataType]) -> Self:
        """Right or.

        Perform element-wise mapping of the input sequence using a conversion function
            and extend the internal data with the mapped values.

        :param other: A sequence of elements to apply the conversion function to.
        :type other: Sequence

        :return: Updated instance with the mapped values added to the internal data.
        :rtype: Self
        """
        data_mapped = map(self.convert_func, other)
        self._data.extend(data_mapped)
        return self

    @nobeartype
    def __ior__(self, other: SequenceNonStr[ConvertibleToDataType]) -> Self:
        """Update the object with the union of itself and another sequence.

        :param other: A sequence of items that can be converted to the same data type
            as the object.
        :type other: SequenceNonStr[ConvertibleToDataType]

        :return: The updated object after the union operation.
        :rtype: Self
        """
        data_mapped = map(self.convert_func, other)
        self._data.extend(data_mapped)
        return self

    @nobeartype
    def __len__(self) -> int:
        """Return the length of the data stored in the StringDataDeque.

        :return: The length of the data.
        :rtype: int
        """
        return len(self._data)

    @nobeartype
    def __getitem__(self, key: SupportsIndex) -> DataType:
        """Get an item from the data using the specified key.

        :param key: The key for retrieving the item from the data.
        :type key: SupportsIndex

        :return: The item corresponding to the key in the data.
        :rtype: DataType
        """
        return self._data[key]

    @nobeartype
    def __setitem__(self, key: SupportsIndex, value: ConvertibleToDataType) -> None:
        """Set the value of a key in the data dictionary.

        :param key: The key to set in the dictionary.
        :type key: SupportsIndex

        :param value: The value to set for the given key.
        :type value: ConvertibleToDataType

        :return: None
        :rtype: None
        """
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
        :param skip_conversion: Flag to skip conversion of items, defaults to False
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
        """Clear the data stored in the object.

        This method clears all elements in the internal data storage.

        :return: None
        :rtype: None
        """
        self._data.clear()

    def draw(self, index: int = -1) -> DataType:
        """Draw and remove an element from the object at the specified index.

        :param index: The index of the element to be drawn and removed.
            Default is -1 (last element).
        :type index: int

        :return: The drawn element from the object.
        :rtype: DataType
        """
        ret = self._data[index]
        del self._data[index]
        return ret


@beartype
class StringDeque(StringDataDeque[str, Builtin_or_DefinesDunderStr]):
    """A class representing a StringDeque."""

    __slots__ = ()

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
        """Initialize the object with the given data and separator.

        :param data: A sequence of non-string objects, a string, or None.
        :type data: Union[Sequence, str, None]

        :param sep: Separator to use when joining the data elements.
        :type sep: str

        :return: None
        :rtype: None
        """
        super().__init__(convert_func=str, format_func=str, data=data, sep=sep)


@beartype
class CircularStringDeque(StringDeque):
    """A circular StringBuffer, overwrites once maxlen reached."""

    __slots__ = ("_size",)

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
        """Initialize CircularStringDeque with a limited size.

        :param size: The maximum size of the data structure.
        :type size: int
        :param data: Initial data to populate the structure (optional).
        :type data: SequenceNonStr[Builtin_or_DefinesDunderStr] |
            Builtin_or_DefinesDunderStr | None
        :param sep: Separator for data elements when initializing (optional).
        :type sep: str

        :return: None
        :rtype: None
        """
        super().__init__(data=data, sep=sep)
        self._size = size
        self._data = deque(self._data, maxlen=self._size)


@beartype
class WORMStringDeque(StringDeque):
    """A class representing a WORM (Write Once Read Many) String Deque.

    This class extends StringDeque and implements WORM (Write Once Read Many)
    functionality. It does not allow modification of existing items once they are added.

    Note: The following methods are not implemented in WORMStringDeque and will raise
        NotImplementedError:

    - __setitem__: Setting items using indexing is not allowed.
    - clear: Clearing all items from the deque is not allowed.
    - __delitem__: Deleting items from the deque is not allowed.

    :raises NotImplementedError: When trying to perform unsupported operations on
        WORMStringDeque.
    """

    __slots__ = ()

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
        """Initialize the object with optional data and separator.

        :param data: Optional data to initialize the object with.
        :type data: SequenceNonStr[Builtin_or_DefinesDunderStr] |
            Builtin_or_DefinesDunderStr | None

        :param sep: Optional separator for the data.
        :type sep: str

        :return: None
        :rtype: None
        """
        super().__init__(data=data, sep=sep)

    def __setitem__(
        self,
        key: SupportsIndex,
        value: Builtin_or_DefinesDunderStr,
    ) -> None:
        """Set the value for a key in the object.

        :param key: The key to set the value for.
        :type key: SupportsIndex

        :param value: The value to set for the key.
        :type value: Builtin_or_DefinesDunderStr

        :return: None

        :raise NotImplementedError: If the method is called and not implemented.
        """
        msg = f"{self.__class__.__qualname__} does not implement {current_func_name()}"
        raise NotImplementedError(
            msg,
        )

    def clear(self) -> None:
        """Clear the object.

        This method is not implemented and will raise a NotImplementedError with a
            message indicating that the method is not implemented.

        :raises NotImplementedError: Method is not implemented in the current class.
        """
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
