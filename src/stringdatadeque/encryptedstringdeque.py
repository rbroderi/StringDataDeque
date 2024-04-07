"""An example subclass of string deque."""

import base64
import binascii
import dataclasses
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from functools import partial

try:
    from typing import Self
except ImportError:  # pragma: no cover
    from typing_extensions import Self  # pragma: no cover
from typing import cast

from beartype import beartype  # pyright: ignore[reportUnknownVariableType]
from Crypto.Cipher import AES  # nosec: B413
from Crypto.Cipher import PKCS1_OAEP  # nosec: B413
from Crypto.PublicKey import (  # nosec: B413 #false positive as we are using pycryptome
    RSA,
)
from Crypto.Random import get_random_bytes  # nosec: B413

from .protocols import Builtin_or_DefinesDunderStr
from .protocols import SequenceNonstrOfStr
from .stringdatadeque import StringDataDeque


@beartype
class Base64Encoded(str):
    """Stores string as base64 encoded."""

    __slots__ = ("__name",)

    @staticmethod
    def is_base64(sb: str | bytes) -> bool:
        """Return true if it is a base64 encoded."""
        try:
            if isinstance(sb, str):
                # If there's any unicode here, an exception will be thrown and the
                # function will return false
                sb = bytes(sb, "ascii")
            return base64.b64encode(base64.b64decode(sb)) == sb
        except (UnicodeEncodeError, binascii.Error):
            return False

    def __get__(self, instance: "RSAMessage | None", owner: type) -> str | Self:
        """Get the base64 encoded string."""
        if instance is None:
            return self
        return instance.__dict__[self.__name]

    def get_decoded(self, instance: "RSAMessage") -> bytes:
        """Return value base64 decoded."""
        return base64.b64decode(instance.__dict__[self.__name])

    def __set__(self, instance: "RSAMessage", value: str | bytes) -> None:
        """Set the value and encode as base64."""
        if value is self:
            return
        if isinstance(value, str):
            if self.is_base64(value):
                instance.__dict__[self.__name] = value
            else:
                instance.__dict__[self.__name] = base64.b64encode(
                    value.encode("utf-8"),
                ).decode("utf-8")
        else:
            instance.__dict__[self.__name] = base64.b64encode(value).decode("utf-8")

    def __set_name__(self, owner: type, name: str) -> None:
        """Set the name to a private dunder name."""
        self.__name = name


@dataclass
@beartype
class RSAMessage:
    """Holds rsa encrypted info and metadata."""

    enc_session_key: str | bytes = field(default=Base64Encoded())
    nonce: str | bytes = field(default=Base64Encoded())
    tag: str | bytes = field(default=Base64Encoded())
    ciphertext: str | bytes = field(default=Base64Encoded())

    def __post_init__(self) -> None:
        """Make sure that all fields are passed."""
        fields = dataclasses.fields(self)
        count = 0
        for the_field in fields:
            if the_field.name not in self.__dict__:
                count += 1
        if count > 0:
            msg = (
                f"{self.__class__.__qualname__}.__init__() missing {count}"
                " required arguments"
            )
            raise TypeError(msg)

    def attribute_as_bytes(self, attribute_name: str) -> bytes:
        """Return the attribute as bytes instead of base64."""
        return cast(Base64Encoded, getattr(RSAMessage, attribute_name)).get_decoded(
            instance=self,
        )


@beartype
class EncryptedStringDeque(StringDataDeque[RSAMessage, Builtin_or_DefinesDunderStr]):
    """Read once write many buffer, using RSA and AES."""

    @staticmethod
    def __keep_encrypted(msg: RSAMessage) -> str:  # pragma: no cover
        return str(msg)

    def __init__(
        self,
        public_key: RSA.RsaKey,
        data: SequenceNonstrOfStr | str | None = None,
        format_func: Callable[[RSAMessage], str] = __keep_encrypted,
        sep: str = "",
    ) -> None:
        """Initialize the ROWMBuffer."""
        self._data: deque[RSAMessage] = deque()
        self.public_key = public_key
        if isinstance(data, str):
            data = [data]
        con_func = partial(self._encrypt, public_key=self.public_key)
        super().__init__(
            convert_func=con_func,
            format_func=format_func,
            data=data,
            sep=sep,
        )

    def _encrypt(
        self,
        msg: Builtin_or_DefinesDunderStr,
        public_key: RSA.RsaKey,
    ) -> RSAMessage:
        """Encrypt the msg."""
        # from https://www.pycryptodome.org/src/examples#encrypt-data-with-rsa
        msg = str(msg)
        session_key = getattr(self, "session_key", None)
        if session_key is None:
            session_key = get_random_bytes(16)
            self.session_key = session_key
            # Encrypt the session key with the public RSA key
            cipher_rsa = PKCS1_OAEP.new(public_key)
            self.enc_session_key = cipher_rsa.encrypt(session_key)
            # Encrypt the data with the AES session key
        # cipher_aes is stateful, need to generate new one each time.
        cipher_aes = AES.new(session_key, AES.MODE_EAX)  # pyright: ignore[reportUnknownMemberType]
        ciphertext, tag = cipher_aes.encrypt_and_digest(msg.encode("utf-8"))

        return RSAMessage(
            self.enc_session_key,
            cipher_aes.nonce,
            tag,
            ciphertext,
        )

    @staticmethod
    def decrypt(msg: RSAMessage, private_key: RSA.RsaKey) -> str:
        """Decrypt to a str."""
        # set RSAMessage to decode
        # msg.decode = True
        # from https://www.pycryptodome.org/src/examples#encrypt-data-with-rsa
        # Decrypt the session key with the private RSA key
        cipher_rsa = PKCS1_OAEP.new(private_key)
        dec_enc_session_key = msg.attribute_as_bytes("enc_session_key")
        dec_nonce = msg.attribute_as_bytes("nonce")
        dec_tag = msg.attribute_as_bytes("tag")
        dec_ciphertext = msg.attribute_as_bytes("ciphertext")
        session_key = cipher_rsa.decrypt(dec_enc_session_key)

        # Decrypt the data with the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX, dec_nonce)  # pyright: ignore[reportUnknownMemberType]
        data = cipher_aes.decrypt_and_verify(dec_ciphertext, dec_tag)
        # msg.decode = False
        return data.decode("utf-8")
