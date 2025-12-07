StringDataDeque
=================
[![Generic badge](https://img.shields.io/badge/license-GPL‐3.0-orange.svg)](https://github.com/rbroderi/StringDataDeque/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/protocol_implements_decorator)](https://pypi.python.org/pypi/StringDataDeque/)
[![Generic badge](https://img.shields.io/badge/mypy-typed-purple.svg)](http://mypy-lang.org/)
[![Generic badge](https://img.shields.io/badge/beartype-runtime_typed-cyan.svg)](https://github.com/beartype/beartype)
[![Generic badge](https://img.shields.io/badge/bandit-checked-magenta.svg)](https://bandit.readthedocs.io/en/latest/)
[![Generic badge](https://img.shields.io/badge/uv-requirements-yellow.svg)](https://github.com/astral-sh/uv)
[![Dynamic TOML Badge](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Frbroderi%2FStringDataDeque%2Fmaster%2Fpyproject.toml&query=%24.project.version&label=Version)](https://github.com/rbroderi/StringDataDeque/releases)

Useful when building a string from data that can be converted into a string, in parts.

## Layout

- `src/stringdatadeque/` – The pure-Python package containing the public API and implementation.
- `examples/` – Small scripts that show common usage patterns.
- `tests/` – Integration and regression tests that guard the API surface.

`import stringdatadeque` exposes a `USING_PURE_PYTHON` flag for backwards compatibility. It is always set to ``True`` now that the package no longer ships a native extension.

## Installation
https://pypi.org/project/StringDataDeque/
```bash
pip install StringDataDeque
```

## Local development

This project is pure Python, so the usual editable install flow works everywhere:

```bash
python -m venv .venv
.venv\Scripts\activate  # PowerShell: .venv\Scripts\Activate.ps1
pip install -e .[dev,optional,docs]
```

To build a distributable wheel:

```bash
uv run python -m build
```

## Uses

This is designed to be a drop-in replacement for when you might want to append to a string in a loop.

### Benefits
* Around 5 times faster than the naive implementation of appending to a string, such as
    ```python
    x = ""
    for x in collection:
        x+="new string"
    ```
* Provides many extra features that help simply code.

## Examples
```python
sd = StringDeque(sep="\n")
for x in collection:
    sd += x
# StringDeque is a specialization of StringDataDeque where conversion func is "str"
# this allows any datatype to be used which can convert to str
sd += 1
print(sd)
```

You can also pipe data into the StringDeque
```python
sd = StringDeque()
sd = [1,2,3,4,5] | sd
# or
sd |= [1,2,3,4,5]
```

StringDataDeque implements the "contains" method so you can search within it
```python
sd = StringDeque(["line_one","line_two"],sep="\n")
if "line_one" in sd:
    print("yes")
```

If you need more control over how data is added to the deque either use StringDataDeque or one of its subclasses.
```python
# convert_func is called when data is added, and format_func is called when data is printed.
int_sdd =StringDataDeque(data="test", convert_func=int, format_func=str,sep=" ")
int_sdd |= ["1","2","3","4","5"]
assert int_sdd[0] == 1
assert str(int_sdd) == "1 2 3 4 5"
```
