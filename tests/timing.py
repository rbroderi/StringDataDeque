# ruff: noqa
# type:ignore
import sys
import timeit
from collections import deque
from functools import partial
from pathlib import Path

SCRIPTROOT = Path(__file__).parent.resolve()
sys.path.append(str(SCRIPTROOT.parent / "src"))
import stringdatadeque  # noqa: E402

# from stringdatadeque import StringDeque


def time(func):
    print(func.__name__)
    time_start = timeit.default_timer()
    ret = func(values_long)
    # calculate the duration
    time_duration = timeit.default_timer() - time_start
    # report the duration
    print(f"Took {time_duration:} seconds")
    return ret


def as_str(values):
    temp = ""
    for i in values:
        temp += f"{i},"
    return temp[:-1]


def as_list(values):
    temp = []
    for i in values:
        temp.append(str(i))
    return ",".join(temp)


def as_deque(values):
    temp = deque()
    for i in values:
        temp.append(str(i))
    return ",".join(temp)


def as_stringdeque(values):
    temp = stringdatadeque.StringDeque(sep=",")
    for i in values:
        temp += i
    return str(temp)


if __name__ == "__main__":
    # a = time(as_str)
    # b = time(as_list)
    # c = time(as_stringdeque)
    # assert a == b == c
    values = range(1000000)
    values_long = range(1000000)
    funcs = (as_str, as_list, as_deque, as_stringdeque)
    for func in funcs:
        print(func.__name__)
        print(min(timeit.Timer(partial(func, values)).repeat(10, 1)))
