SHELL := /bin/bash
PACKAGE_SLUG=src/stringdatadeque
ifdef CI
	PYTHON_PYENV :=
	PYTHON_VERSION := $(shell python --version|cut -d" " -f2)
else
	PYTHON_PYENV := pyenv
	PYTHON_VERSION := $(shell cat .python-version)
endif
PYTHON_SHORT_VERSION := $(shell echo $(PYTHON_VERSION) | grep -o '[0-9].[0-9]*')

ifeq ($(USE_SYSTEM_PYTHON), true)
	PYTHON_PACKAGE_PATH:=$(shell python -c "import sys; print(sys.path[-1])")
	PYTHON_ENV :=
	PYTHON := python
	PYTHON_VENV :=
else
	PYTHON_PACKAGE_PATH:=.venv/lib/python$(PYTHON_SHORT_VERSION)/site-packages
	PYTHON_ENV :=  . .venv/bin/activate &&
	PYTHON := . .venv/bin/activate && python
	PYTHON_VENV := .venv
endif

# Used to confirm that pip has run at least once
PACKAGE_CHECK:=$(PYTHON_PACKAGE_PATH)/build
PYTHON_DEPS := $(PACKAGE_CHECK)

.PHONY: help
help:  ## Print this help menu
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: all
all: $(PACKAGE_CHECK) ##all

.PHONY: install
install: $(PYTHON_PYENV) $(PYTHON_VENV) pip ##install into the venv

.venv:
	python -m venv .venv

.PHONY: pyenv
pyenv:
	pyenv install --skip-existing $(PYTHON_VERSION)

.PHONY: pip
pip: $(PYTHON_VENV)
	$(PYTHON) -m pip install -e .[dev,optional]

$(PACKAGE_CHECK): $(PYTHON_VENV)
	$(PYTHON) -m pip install -e .[dev,optional]

.PHONY: pre-commit_install
pre-commit_install:
	pre-commit install

.PHONY: setup_autodoc
setup_autodoc: ## setup sphynx autodoc
	sphinx-apidoc -f -o docs/source ${PACKAGE_SLUG}


#
# Formatting
#
.PHONY: chores
chores: validate_pyproject ruff_fixes black_fixes dapperdata_fixes tomlsort_fixes docs ## run all chores

.PHONY: validate pyproject
validate_pyproject: ## validate pyproject.toml
	$(PYTHON) -m validate_pyproject pyproject.toml

.PHONY: ruff_fixes
ruff_fixes: ## run ruff and fix
	$(PYTHON) -m ruff check . --fix

.PHONY: black_fixes
black_fixes: ## run ruff formatting
	$(PYTHON) -m ruff format .

.PHONY: dapperdata_fixes
dapperdata_fixes: ## run dapperdata fixes
	$(PYTHON) -m dapperdata.cli pretty . --no-dry-run

.PHONY: tomlsort_fixes
tomlsort_fixes: ## run tomlsort fixes
	$(PYTHON_ENV) toml-sort $$(find . -not -path "./.venv/*" -not -path "./.tox/*" -name "*.toml") -i

.PHONY: docs
docs: ## generate docs
	$(MAKE) -C ./docs clean html

#
# Testing
#
.PHONY: tests
tests: install pytest ruff_check black_check mypy dapperdata_check tomlsort_check ## run all tests

.PHONY: pytest
pytest: ## run pytest
	$(PYTHON) -m pytest --cov=./${PACKAGE_SLUG} --cov-report=term-missing tests

.PHONY: pytestvv
pytestvv: ## run pytest verbose
	$(PYTHON) -m pytest -vv --cov=./${PACKAGE_SLUG} --cov-report=term-missing tests

.PHONY: pytest_loud
pytest_loud: ## run pytest show strings
	$(PYTHON) -m pytest -s --cov=./${PACKAGE_SLUG} --cov-report=term-missing tests

.PHONY: ruff_check
ruff_check: ## run ruff in check mode
	$(PYTHON) -m ruff check

.PHONY: black_check
black_check: ## run ruff format in check mode
	$(PYTHON) -m ruff format . --check

.PHONY: mypy
mypy: ## run mypy check
	$(PYTHON) -m mypy ${PACKAGE_SLUG}

.PHONY: dapperdata_check
dapperdata_check: ## run dapperdata check
	$(PYTHON) -m dapperdata.cli pretty .

.PHONY: tomlsort_check
tomlsort_check: ## run tomlsort_check
	$(PYTHON_ENV) toml-sort $$(find . -not -path "./.venv/*" -not -path "./.tox/*" -name "*.toml") --check
#
# Dependencies
#

.PHONY: rebuild_dependencies
rebuild_dependencies: ## rebuild dependencies
	$(PYTHON) -m uv pip compile --output-file=requirements.txt pyproject.toml
	$(PYTHON) -m uv pip compile --output-file=requirements-dev.txt --extra=dev pyproject.toml
	$(PYTHON) -m uv pip compile --output-file=requirements-optional.txt --extra=optional pyproject.toml

.PHONY: dependencies
dependencies: requirements.txt requirements-dev.txt requirements-optional.txt

requirements.txt: $(PACKAGE_CHECK) pyproject.toml ## generate requirements.txt
	$(PYTHON) -m uv pip compile --upgrade --output-file=requirements.txt pyproject.toml

requirements-dev.txt: $(PACKAGE_CHECK) pyproject.toml ## generate dev requirements.txt
	$(PYTHON) -m uv pip compile --upgrade --output-file=requirements-dev.txt --extra=dev pyproject.toml

requirements-optional.txt: $(PACKAGE_CHECK) pyproject.toml ## generate option requirements.txt
	$(PYTHON) -m uv pip compile --upgrade --output-file=requirements-optional.txt --extra=optional pyproject.toml


#
# Packaging
#

.PHONY: build ## build package
build: $(PACKAGE_CHECK)
	$(PYTHON) -m build
