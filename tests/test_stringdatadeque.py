# ruff: noqa
# type:ignore
# import sys

# print(sys.path)
import textwrap

import pytest
from stringdatadeque import CircularStringDeque
from stringdatadeque import StringDataDeque
from stringdatadeque import StringDeque
from stringdatadeque import WORMStringDeque


def create_stringdeque(value=None):
    return StringDeque(sep="\n", data=value)


def create_circularstringdeque(value=None):
    return CircularStringDeque(size=10, sep="\n", data=value)


def create_wormstringdeque(value=None):
    return WORMStringDeque(sep="\n", data=value)


def test_init():
    a = StringDataDeque(data="test", convert_func=str, format_func=str)
    b = StringDataDeque(data=["test"], convert_func=str, format_func=str)
    assert a[0] == "test"
    assert b[0] == "test"


@pytest.mark.parametrize(
    "stringdeque_func",
    [
        create_stringdeque,
        create_circularstringdeque,
        create_wormstringdeque,
    ],
)
class Test_For_all:
    @staticmethod
    def test_init(stringdeque_func):
        a = stringdeque_func("test")
        b = stringdeque_func(1)
        c = stringdeque_func(["test"])
        assert a[0] == "test"
        assert b[0] == "1"
        assert c[0] == "test"

    @staticmethod
    def test_empty(stringdeque_func):
        stringdeque = stringdeque_func()
        assert str(stringdeque) == ""

    @staticmethod
    def test_add(stringdeque_func):
        stringdeque = stringdeque_func()
        stringdeque = stringdeque + "Line 1"
        stringdeque = stringdeque + 2
        assert str(stringdeque) == "Line 1\n2"

    @staticmethod
    def tests_radd(stringdeque_func):
        stringdeque = stringdeque_func()
        stringdeque = "Line 1" + stringdeque
        stringdeque = 2 + stringdeque
        assert str(stringdeque) == "Line 1\n2"

    @staticmethod
    def test_iadd(stringdeque_func):
        stringdeque = stringdeque_func()
        stringdeque += "Line 1"
        stringdeque += 2
        assert str(stringdeque) == "Line 1\n2"

    @staticmethod
    def test_ror(stringdeque_func):
        stringdeque = stringdeque_func()
        stringdeque = ["Line1", "Line2"] | stringdeque
        stringdeque = [3, 4] | stringdeque
        assert str(stringdeque) == "Line1\nLine2\n3\n4"

    @staticmethod
    def test_len(stringdeque_func):
        stringdeque = stringdeque_func()
        stringdeque = stringdeque + "Line1"
        stringdeque += 2
        stringdeque = ["Line3", 4] | stringdeque
        stringdeque |= [5, "Line6"]
        assert len(stringdeque) == 6

    @staticmethod
    def test_getitem(stringdeque_func):
        stringdeque = stringdeque_func()
        stringdeque += "test"
        stringdeque += 1
        assert stringdeque[0] == "test"
        assert stringdeque[1] == "1"

    @staticmethod
    def test_str(stringdeque_func):
        stringdeque = stringdeque_func()
        stringdeque += "first line"
        stringdeque = stringdeque + "line 2"
        stringdeque = [
            "several more",
            "and another",
        ] | stringdeque
        stringdeque |= ["final"]
        assert str(stringdeque) == textwrap.dedent("""\
    first line
    line 2
    several more
    and another
    final""")

    @staticmethod
    def test_draw(stringdeque_func):
        stringdeque = stringdeque_func()
        stringdeque += "line 1"
        msg = stringdeque.draw()
        assert isinstance(msg, str)
        assert msg == "line 1"

    @staticmethod
    def test_insert_with_conv_func(stringdeque_func):
        stringdeque = stringdeque_func()

        def conv_func(obj: int) -> str:
            return str(obj * 2)

        stringdeque.insert([1, 2, 3, 4, 5, 6, 7, 8, 9], conv_func)
        assert str(stringdeque) == textwrap.dedent("""\
    2
    4
    6
    8
    10
    12
    14
    16
    18""")

    @staticmethod
    def test_insert_without_conv_func(stringdeque_func):
        stringdeque = stringdeque_func()
        stringdeque.insert([1, 2, 3, 4, 5, 6, 7, 8, 9])
        assert str(stringdeque) == textwrap.dedent("""\
    1
    2
    3
    4
    5
    6
    7
    8
    9""")

    @staticmethod
    def test_check_insert_no_convert_types(stringdeque_func):
        stringdeque = stringdeque_func()

        class Fail:
            pass

        stringdeque += "test"
        with pytest.raises(TypeError):
            stringdeque.insert(None, func=None)
        with pytest.raises(TypeError):
            stringdeque.insert(Fail(), func=None)
        assert str(stringdeque) == "test"

    @staticmethod
    def test_insert_no_pre_or_conv(stringdeque_func):
        stringdeque = stringdeque_func()
        stringdeque.insert([1, 2], pre_process_func=None, skip_conversion=True)
        stringdeque.insert(1, pre_process_func=None, skip_conversion=True)
        stringdeque.insert(1, pre_process_func=str, skip_conversion=False)
        assert stringdeque[0] == 1

    @staticmethod
    def test_str_format(stringdeque_func):
        stringdeque = stringdeque_func()
        stringdeque.sep = "!"
        stringdeque |= [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        assert f"{stringdeque:sep='\n'}" == textwrap.dedent("""\
            1
            2
            3
            4
            5
            6
            7
            8
            9
            0""")
        assert f"{stringdeque:>24}" == "     1!2!3!4!5!6!7!8!9!0"

    @staticmethod
    def test_in(stringdeque_func):
        stringdeque = stringdeque_func()
        stringdeque.sep = ","
        stringdeque |= [1, 2]
        assert "1" in stringdeque
        assert "1,2" in stringdeque


# def test_or(stringdeque):
#     stringdeque = stringdeque | ["Line1", "Line2"]
#     stringdeque = stringdeque | [3, 4]
#     assert str(stringdeque) == "Line1\nLine2\n3\n4"


@pytest.mark.parametrize(
    "stringdeque",
    [create_stringdeque(), create_circularstringdeque()],
)
def test_setitem(stringdeque):
    with pytest.raises(IndexError):
        stringdeque[0] = "test"
    with pytest.raises(IndexError):
        stringdeque[1] = 1
    stringdeque += "old"
    assert stringdeque[0] == "old"
    stringdeque[0] = "new"
    assert stringdeque[0] == "new"


def test_StringDeque():
    temp = StringDeque("test")
    assert temp is not None


@pytest.mark.parametrize(
    "stringdeque",
    [create_stringdeque(), create_circularstringdeque()],
)
def test_clear(stringdeque):
    stringdeque += "line 1"
    stringdeque += "line 2"
    assert len(stringdeque) == 2
    assert str(stringdeque) != ""
    stringdeque.clear()
    assert len(stringdeque) == 0
    assert str(stringdeque) == ""


def testCircularStringDeque():
    test = CircularStringDeque(size=3, sep="\n")
    test += "1"
    test += "2"
    test |= [3, 4]
    assert len(test) == 3
    assert test[-1] == "4"


def test_WORMStringDeque_not_implemented():
    temp = WORMStringDeque(data="starting")
    with pytest.raises(NotImplementedError):
        temp[0] = "should not work"
    with pytest.raises(NotImplementedError):
        temp.clear()
    with pytest.raises(NotImplementedError):
        del temp[0]
