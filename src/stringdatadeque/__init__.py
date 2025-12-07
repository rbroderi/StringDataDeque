"""Public entry point for StringDataDeque (pure Python implementation)."""

from __future__ import annotations

import warnings as _warnings
from typing import TYPE_CHECKING
from typing import Final

from .stringdatadeque import CircularStringDeque
from .stringdatadeque import StringDataDeque
from .stringdatadeque import StringDeque as _PureStringDeque
from .stringdatadeque import WORMStringDeque

try:
    from .encryptedstringdeque import EncryptedStringDeque as _EncryptedStringDeque
    from .encryptedstringdeque import RSAMessage as _RSAMessage
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    _EncryptedStringDeque = None  # type: ignore[assignment]
    _RSAMessage = None  # type: ignore[assignment]

USING_PURE_PYTHON: Final[bool] = True

StringDeque = _PureStringDeque
PureStringDeque = _PureStringDeque
EncryptedStringDeque = _EncryptedStringDeque
RSAMessage = _RSAMessage

if EncryptedStringDeque is None:  # pragma: no cover - optional dependency
    _warnings.warn(
        "PyCryptodome required for EncryptedStringDeque",
        ImportWarning,
        stacklevel=2,
    )
    EncryptedStringDeque = None  # type: ignore[assignment]
    RSAMessage = None  # type: ignore[assignment]

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from .stringdatadeque import StringDeque as _TypingStringDeque

    StringDeque = _TypingStringDeque

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
