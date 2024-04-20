# ruff: noqa
# type:ignore
# pylint: skip-file
import sys
import timeit
from collections import deque
from functools import partial
from pathlib import Path
import random
import argparse

SCRIPTROOT = Path(__file__).parent.resolve()
sys.path.append(str(SCRIPTROOT.parent / "src"))
import stringdatadeque  # noqa: E402

# from stringdatadeque import StringDeque


def time(func):
    print(func.__name__)
    time_start = timeit.default_timer()
    values_long = range(10000000)
    ret = func(values_long)
    # calculate the duration
    time_duration = timeit.default_timer() - time_start
    # report the duration
    print(f"Took {time_duration:} seconds")
    return ret


def as_str(values):
    temp = ""
    for i in values:
        temp += f"{random.randint(0,1000)}"  # nosec: B311
    return temp


def as_list(values):
    temp = []
    for i in values:
        temp.append(f"{random.randint(0,1000)}")  # nosec: B311
    return ",".join(temp)


def as_deque(values):
    temp = deque()
    for i in values:
        temp.append(f"{random.randint(0,1000)}")  # nosec: B311
    return ",".join(temp)


def as_stringdeque(values):
    temp = stringdatadeque.StringDeque(sep=",")
    for i in values:
        temp += random.randint(0, 1000)  # nosec: B311
    return str(temp)


def main() -> int:
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--profile",
            help="run in profile mode",
            action="store_true",
        )
        args = parser.parse_args()
        values = range(100000)
        values_long = range(100000)
        funcs = (
            (as_stringdeque,)
            if args.profile
            else (as_str, as_list, as_deque, as_stringdeque)
        )
        for func in funcs:
            print(func.__name__)
            print(min(timeit.Timer(partial(func, values)).repeat(10, 5)))
    except Exception as e:
        print(e)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
