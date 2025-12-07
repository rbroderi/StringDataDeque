# StringDataDeque

StringDataDeque is a tiny utility package for building strings from heterogeneous
objects without paying the quadratic cost of `+=` in tight loops. It exposes the
`StringDataDeque` generic plus a convenience `StringDeque` specialization that
accepts any object with a useful `__str__` implementation.

- **Repository**: https://github.com/rbroderi/StringDataDeque
- **Python package**: `StringDataDeque`
- **Docs toolchain**: MkDocs + Material with mkdocstrings for the API section

## Highlights

- Works entirely in pure Python and depends only on the standard library plus
  `beartype` for lightweight runtime validation.
- Provides an ergonomic `StringDeque` facade for everyday use while keeping the
  fully generic `StringDataDeque` class available for advanced scenarios.
- Implements Pythonic protocols (`__contains__`, `__ior__`, `__ror__`, slicing)
  so it can act like a deque, a buffer, or a streaming string builder.
- Ships typed stubs (`py.typed`) and runtime checks so the same codebase is
  happy in both static and dynamic environments.

## Quick Example

```python
from stringdatadeque import StringDeque

records = ["alpha", "beta", "gamma"]
log = StringDeque(sep="\n")
for item in records:
    log += item
log += 42  # automatically converted to a string

print(str(log))
# alpha
# beta
# gamma
# 42
```

## Project Layout

- `src/stringdatadeque/` – pure-Python implementation and public API.
- `tests/` – regression suite covering the deque variants.
- `docs/` – these MkDocs sources; run `uv run mkdocs serve` in the repository
  root for live previews.
- `benchmarks/` – simple throughput comparisons against naive concatenation.
