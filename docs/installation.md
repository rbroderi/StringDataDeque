# Installation

## From PyPI

Install the published wheel or source distribution directly from PyPI:

```bash
pip install StringDataDeque
```

The package is pure Python, so no platform-specific toolchains are required.

## Editable Install for Development

Clone the repository and install the project plus its optional extras inside a
virtual environment. The examples below use
[`uv`](https://github.com/astral-sh/uv), but any virtualenv workflow works.

```bash
git clone https://github.com/rbroderi/StringDataDeque.git
cd StringDataDeque
uv venv
uv pip install -e .[dev,optional,docs]
```

This gives you the test suite, benchmarking helpers, optional crypto support,
and the MkDocs toolchain used to build this site.

## Building Distributions

Produce a wheel (and sdist) using `build` via `uv`:

```bash
uv run python -m build
```

Artifacts are written to `dist/`. Upload them with `twine` or any preferred
publisher.

## Building the Documentation

The documentation now uses MkDocs with the Material theme. After installing the
`docs` extra you can render the site locally:

```bash
uv run mkdocs serve
```

The command starts a live-reload server on `http://127.0.0.1:8000`. Use `uv run
mkdocs build` to generate the static site without launching the dev server.
