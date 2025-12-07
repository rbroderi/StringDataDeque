"""Public entry point for StringDataDeque (pure Python implementation)."""

from __future__ import annotations

import warnings as _warnings
from typing import TYPE_CHECKING
from typing import Final

from .stringdatadeque import CircularStringDeque
from .stringdatadeque import StringDataDeque
from .stringdatadeque import StringDeque
from .stringdatadeque import WORMStringDeque

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from .encryptedstringdeque import EncryptedStringDeque
    from .encryptedstringdeque import RSAMessage
else:  # pragma: no cover - runtime optional import
    try:
        from .encryptedstringdeque import EncryptedStringDeque
        from .encryptedstringdeque import RSAMessage
    except ModuleNotFoundError:
        EncryptedStringDeque = None  # type: ignore[assignment]
        RSAMessage = None  # type: ignore[assignment]

USING_PURE_PYTHON: Final[bool] = True

PureStringDeque = StringDeque

if (
    not TYPE_CHECKING
) and EncryptedStringDeque is None:  # pragma: no cover - optional dependency
    _warnings.warn(
        "PyCryptodome required for EncryptedStringDeque",
        ImportWarning,
        stacklevel=2,
    )
    EncryptedStringDeque = None  # type: ignore[assignment]
    RSAMessage = None  # type: ignore[assignment]

__all__ = [
    "USING_PURE_PYTHON",
    "CircularStringDeque",
    "EncryptedStringDeque",
    "PureStringDeque",
    "RSAMessage",
    "StringDataDeque",
    "StringDeque",
    "WORMStringDeque",
]
