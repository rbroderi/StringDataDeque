# API Reference

Install the package in editable mode so mkdocstrings can import the latest
sources:

```bash
uv pip install -e .[docs]
```

## Package Module

::: stringdatadeque
    handler: python
    options:
      members: true
      show_source: false
      separate_signature: true

## Core Implementation

::: stringdatadeque.stringdatadeque
    handler: python
    options:
      members: true
      show_source: false
      separate_signature: true
      docstring_style: google

## Optional Helpers

::: stringdatadeque.encryptedstringdeque
    handler: python
    options:
      members: true
      show_source: false

## Protocol Definitions

::: stringdatadeque.protocols
    handler: python
    options:
      members: true
      show_source: false
