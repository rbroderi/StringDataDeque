"""Main package for stringdatadeque."""

from .stringdatadeque import CircularStringDeque as CircularStringDeque
from .stringdatadeque import StringDataDeque as StringDataDeque
from .stringdatadeque import StringDeque as StringDeque
from .stringdatadeque import WORMStringDeque as WORMStringDeque

# PyCryptodome required for EncryptStringDeque
try:
    import Crypto as __Crypto  # noqa: F401 #pyright: ignore[reportUnusedImport]

    from .encryptedstringdeque import EncryptedStringDeque as EncryptedStringDeque
    from .encryptedstringdeque import RSAMessage as RSAMessage
except ModuleNotFoundError:
    import warnings as __warnings

    __warnings.warn(
        "PyCryptodome required for EncryptedStringDeque",
        ImportWarning,
        stacklevel=0,
    )
    del __warnings
