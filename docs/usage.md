# Usage

This page mirrors the most common patterns from the README and the test suite.
All examples assume `uv pip install -e .` so that mkdocstrings can import the
local sources.

## Streaming Appends

`StringDeque` is optimized for the classic "append fragments in a loop" use
case while still accepting arbitrary data types thanks to the `str` conversion.

```python
from stringdatadeque import StringDeque

parts = ["alpha", "beta", "gamma"]
buffer = StringDeque(sep="\n")

for chunk in parts:
    buffer += chunk
buffer += 123  # automatically converted via str()

print(buffer)
```

Compared to `result += chunk` in a loop this approach avoids repeatedly
reallocating intermediate strings and is typically ~5x faster for large payloads.

## Bulk Ingestion with `|` or `|=`

The deque implements the bitwise-or operators for convenience. You can pipe a
sequence into a deque or update an existing instance in place:

```python
from stringdatadeque import StringDeque

buf = StringDeque()
buf = [1, 2, 3, 4] | buf
buf |= [5, 6, 7]
```

## Membership Tests

`StringDeque` implements `__contains__` so you can search the rendered output:

```python
from stringdatadeque import StringDeque

log = StringDeque(["line_one", "line_two"], sep="\n")
if "line_one" in log:
    print("found it")
```

## Advanced Conversion Hooks

Drop down to `StringDataDeque` if you need separate conversion / formatting
logic or wish to work with types other than strings internally.

```python
from stringdatadeque import StringDataDeque

ints = StringDataDeque(
    data="1",
    convert_func=int,
    format_func=str,
    sep=", ",
)
ints |= ["2", "3", "4"]
assert ints[0] == 1
assert str(ints) == "1, 2, 3, 4"
```
