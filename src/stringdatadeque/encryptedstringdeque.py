"""An example subclass of string deque."""

import base64
import binascii
from collections import deque
from collections.abc import Callable
from functools import partial

try:
    from typing import Self
except ImportError:  # pragma: no cover
    from typing_extensions import Self  # pragma: no cover
from typing import cast

from beartype import beartype
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
    """A class representing a Base64 encoded string."""

    __slots__ = ("__name",)

    def __init__(self, name_: str) -> None:
        """Initialize the base64encoded string."""
        self.__name = name_

    @staticmethod
    def is_base64(sb: str | bytes) -> bool:
        """Check if the input string or bytes object is a valid Base64 encoded string.

        :param sb: The input string or bytes object to be checked.
        :type sb: str or bytes

        :return: True if the input is a valid Base64 encoded string, False otherwise.
        :rtype: bool
        """
        try:
            if isinstance(sb, str):
                # If there's any unicode here, an exception will be thrown and the
                # function will return false
                sb = bytes(sb, "ascii")
            return base64.b64encode(base64.b64decode(sb)) == sb
        except (UnicodeEncodeError, binascii.Error):
            return False

    def __get__(self, instance: "RSAMessage | None", owner: type) -> str | Self:
        """Get the base64 encoded string.

        :param instance: The instance to get the value for.
        :type instance: RSAMessage or None

        :param owner: The owner type of the descriptor.
        :type owner: type

        :return: The value of the descriptor for the instance.
        :rtype: str or Self
        """
        if instance is None:
            return self
        return getattr(instance, self.__name)

    def get_decoded(self, instance: "RSAMessage") -> bytes:
        """Get value base64 decoded.

        :param instance: An instance of RSAMessage.
        :type instance: RSAMessage

        :return: The decoded message as bytes.
        :rtype: bytes
        """
        return base64.b64decode(getattr(instance, self.__name))

    def __set__(self, instance: "RSAMessage", value: str | bytes) -> None:
        """Set the value and encode as base64.

        :param instance: The instance of the class where the descriptor attribute is
            set.
        :type instance: RSAMessage

        :param value: The value to be set, either a string or bytes.
        :type value: str or bytes

        :return: None
        :rtype: None
        """
        if value is self:
            return
        if isinstance(value, str):
            if self.is_base64(value):
                setattr(instance, self.__name, value)
                # instance.__dict__[self.__name] = value
            else:
                setattr(
                    instance,
                    self.__name,
                    base64.b64encode(
                        value.encode("utf-8"),
                    ).decode("utf-8"),
                )
        else:
            setattr(instance, self.__name, base64.b64encode(value).decode("utf-8"))


# @beartype errors?
class RSAMessage:
    """A dataclass representing an RSA message.

    :param enc_session_key: The encrypted session key.
    :type enc_session_key: str | bytes
    :param nonce: The nonce value.
    :type nonce: str | bytes
    :param tag: The tag value.
    :type tag: str | bytes
    :param ciphertext: The encrypted ciphertext.
    :type ciphertext: str | bytes
    """

    __slots__ = ("_enc_session_key", "_nonce", "_tag", "_ciphertext")

    enc_session_key: str | bytes = Base64Encoded("_enc_session_key")
    nonce: str | bytes = Base64Encoded("_nonce")
    tag: str | bytes = Base64Encoded("_tag")
    ciphertext: str | bytes = Base64Encoded("_ciphertext")

    @beartype
    def __init__(
        self,
        enc_session_key: str | bytes,
        nonce: str | bytes,
        tag: str | bytes,
        ciphertext: str | bytes,
    ) -> None:
        """Initialize the object.

        :param enc_session_key: The encrypted session key.
        :type enc_session_key: str or bytes

        :param nonce: The nonce value.
        :type nonce: str or bytes

        :param tag: The tag value.
        :type tag: str or bytes

        :param ciphertext: The encrypted ciphertext.
        :type ciphertext: str or bytes

        :return: None
        :rtype: None
        """
        self.enc_session_key = enc_session_key  # type: ignore[misc] # noqa: PLE0237
        self.nonce = nonce  # type: ignore[misc] # noqa: PLE0237
        self.tag = tag  # type: ignore[misc] # noqa: PLE0237
        self.ciphertext = ciphertext  # type: ignore[misc] # noqa: PLE0237

    @beartype
    def attribute_as_bytes(self, attribute_name: str) -> bytes:
        """Return the decoded attribute value as bytes.

        :param attribute_name: Name of the attribute containing a Base64 encoded value.
        :type attribute_name: str

        :return: The decoded attribute value as bytes.
        :rtype: bytes
        """
        return cast(Base64Encoded, getattr(RSAMessage, attribute_name)).get_decoded(
            instance=self,
        )

    @beartype
    def __str__(self) -> str:
        """Return the string representation of the object.

        :return: The string representation of the object.
        :rtype: str
        """
        return f"{self.enc_session_key=}{self.nonce=}{self.tag=}{self.ciphertext=}"

    @beartype
    def __eq__(self, value: object) -> bool:
        """Check if the object is equal to another object.

        :param value: The object to compare to.
        :type value: object

        :return: True if the objects are equal, False otherwise.
        :rtype: bool
        """
        if not isinstance(value, RSAMessage):
            return False
        return (
            self.enc_session_key == value.enc_session_key
            and self.nonce == value.nonce
            and self.tag == value.tag
            and self.ciphertext == value.ciphertext
        )


@beartype
class EncryptedStringDeque(StringDataDeque[RSAMessage, Builtin_or_DefinesDunderStr]):
    """Read once write many buffer, using RSA and AES.

    :param public_key: The public key used for encryption.
    :type public_key: RSA.RsaKey
    :param data: The initial data to be stored in the deque.
    :type data: SequenceNonstrOfStr | str | None
    :param format_func: The function used to format the encrypted data.
    :type format_func: Callable[[RSAMessage], str]
    :param sep: The separator used when joining the strings.
    :type sep: str
    """

    __slots__ = ("type", "public_key", "session_key", "enc_session_key", "_data")

    @staticmethod
    def __keep_encrypted(msg: RSAMessage) -> str:  # pragma: no cover
        """Keep the message encrypted.

        :param msg: The encrypted message.
        :type msg: RSAMessage

        :return: The encrypted message as a string.
        :rtype: str
        """
        return str(msg)

    def __init__(
        self,
        public_key: RSA.RsaKey,
        data: SequenceNonstrOfStr | str | None = None,
        format_func: Callable[[RSAMessage], str] = __keep_encrypted,
        sep: str = "",
    ) -> None:
        """Initialize the object.

        :param public_key: The public key used for encryption.
        :type public_key: RSA.RsaKey

        :param data: The data to be encrypted. Can be a single string or a list of
            strings. Defaults to None.
        :type data: Union[str, List[str], None]

        :param format_func: The function used to format the encrypted data.
            Defaults to __keep_encrypted.
        :type format_func: Callable[[RSAMessage], str]

        :param sep: The separator used to join multiple encrypted messages.
            Defaults to ''.
        :type sep: str

        :return: None
        :rtype: None
        """
        self.session_key: bytes
        self.enc_session_key: bytes
        self._data: deque[RSAMessage] = deque()
        self.public_key = public_key
        if isinstance(data, str):
            data = (data,)
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
        """Encrypt a message using RSA and AES encryption.

        From https://www.pycryptodome.org/src/examples#encrypt-data-with-rsa.

        :param msg: The message to be encrypted.
        :type msg: str

        :param public_key: The public key used for encryption.
        :type public_key: RSA.RsaKey

        :return: An RSAMessage object containing the encrypted message.
        :rtype: RSAMessage
        """
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
        # """Decrypt to a str."""
        """Decrypt a message using RSA encryption and AES decryption.

        From https://www.pycryptodome.org/src/examples#encrypt-data-with-rsa.

        :param msg: An RSAMessage object containing encrypted data.
        :type msg: RSAMessage

        :param private_key: Private key used for decryption.
        :type private_key: RSA.RsaKey

        :return: The decrypted message as a string.
        :rtype: str
        """
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
