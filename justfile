set ignore-comments := true

PACKAGE_SLUG := "src/stringdatadeque"

# print list of commands
help:
    @just --list --unsorted

# install into the venv
install:
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"; \
    if ! command -v uv >/dev/null 2>&1; then \
        curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null; \
        export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"; \
    fi
    @# $(PYTHON_PYENV)
    {{ if env("CI", "false") != "false" { "" } else { "pyenv install --skip-existing $PYTHON_VERSION " } }}
    @# $(PYTHON_VENV)
    {{ if env("USE_SYSTEM_PYTHON", "false") != "false" { "" } else { "python -m venv .venv" } }}
    @# pip
    PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH" uv run python -m pip install -e .[dev,optional,docs]

# Install pre-commit
pre-commit_install:
    pre-commit install

# copy as template
copy_as_template DEST:
    rsync -r --exclude .mypy_cache --exclude .pytest_cache --exclude .ruff_cache --exclude .tox --exclude .venv --exclude StringDataDeque* --exclude .git --exclude stringdatadeque* ./ {{ DEST }}
    cd {{ DEST }} && git init . && git commit --allow-empty -m 'Make initial root commit'

# profiling
profile:
    python -m cProfile -s time -o timing.prof tests/timing.py --profile
    snakeviz timing.prof

#
# Formatting
#

# Run all linting and fixes
fixes: validate_pyproject ruff_fixes ruff_format_fixes pylint dapperdata_fixes tomlsort_fixes docs pytest

_fixes_no_ruff: validate_pyproject dapperdata_fixes tomlsort_fixes docs pytest update_dependencies_quiet

# Validate pyproject.toml format
validate_pyproject:
    uv run python -m validate_pyproject pyproject.toml

# Run pylint
pylint:
    uv run python -m pylint {{ PACKAGE_SLUG }}

# Run Ruff and fix
ruff_fixes:
    uv run python -m ruff check . --fix

alias black_check := ruff_format_fixes

# Run Ruff format fixes
ruff_format_fixes:
    uv run python -m ruff format .

# Run dapperdata fixes
dapperdata_fixes:
    uv run python -m dapperdata.cli pretty . --no-dry-run

# Run Tomlsort fixes
tomlsort_fixes:
    uv run toml-sort `find . -not -path "./.venv/*" -not -path "./.tox/*" -name "*.toml"` -i

# Generate Docs
docs:
    make -C ./docs clean html

#
# Testing
#

# Run all tests
tests: install pytest ruff_check ruff_format_check mypy dapperdata_check tomlsort_check

# Run Pytest
pytest:
    uv run pytest --cov=./{{ PACKAGE_SLUG }} --cov-report=term-missing tests

# Run Pytest verbose
pytestvv:
    uv run pytest -vv --cov=./{{ PACKAGE_SLUG }} --cov-report=term-missing tests

# Run pytest show strings
pytest_loud:
    uv run pytest -vv -rA --cov=./{{ PACKAGE_SLUG }} --cov-report=term-missing tests

# Run ruff in check mode
ruff_check:
    uv run python -m ruff check

# Run ruff format in check mode
ruff_format_check:
    uv run python -m ruff format . --check

# Run mypy check
mypy:
    uv run python -m mypy {{ PACKAGE_SLUG }}

# Run dapperdata check
dapperdata_check:
    uv run python -m dapperdata.cli pretty .

# Run tomlsort_check
tomlsort_check:
    uv run toml-sort `find . -not -path "./.venv/*" -not -path "./.tox/*" -name "*.toml"` --check

#
# Dependencies
#

# Rebuild dependencies
rebuild_dependencies:
    uv run python -m pip compile --output-file=requirements.txt pyproject.toml
    uv run python -m pip compile --output-file=requirements-dev.txt --extra=dev pyproject.toml
    uv run python -m pip compile --output-file=requirements-optional.txt --extra=optional pyproject.toml

# Update dependencies
update_dependencies:
    uv run python -m pip compile --upgrade --output-file=requirements.txt pyproject.toml
    uv run python -m pip compile --upgrade --output-file=requirements-dev.txt --extra=dev pyproject.toml
    uv run python -m pip compile --upgrade --output-file=requirements-optional.txt --extra=optional pyproject.toml

update_dependencies_quiet:
    uv run python -m pip compile --upgrade --output-file=requirements.txt pyproject.toml > /dev/null
    uv run python -m pip compile --upgrade --output-file=requirements-dev.txt --extra=dev pyproject.toml > /dev/null
    uv run python -m pip compile --upgrade --output-file=requirements-optional.txt --extra=optional pyproject.toml > /dev/null

#

# Build package
build: install
    uv run python -m build
