"""Tiny demo showing the pure-Python backend in action."""

from __future__ import annotations

from stringdatadeque import PureStringDeque
from stringdatadeque import StringDeque


def main() -> None:
    """Demonstrate the high-level ``StringDeque`` APIs."""
    deque = StringDeque(sep=" | ")
    deque += "hello"
    deque = deque + "world"
    ["from", "python"] | deque
    print("backend: pure python")
    print(str(deque))

    pure = PureStringDeque(data=["fall", "back"], sep=",")
    print("pure fallback:", pure)


if __name__ == "__main__":
    main()
