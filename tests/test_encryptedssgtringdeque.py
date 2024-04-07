# ruff: noqa
# type:ignore
# import sys

# print(sys.path)
import base64
from functools import partial
from pathlib import Path

import pytest

try:
    from Crypto.PublicKey import (  # nosec: B413 #false positive as we are using pycryptome
        RSA,
    )
except ModuleNotFoundError:
    pytest.skip(allow_module_level=True)
from stringdatadeque import EncryptedStringDeque
from stringdatadeque import RSAMessage
from stringdatadeque.encryptedstringdeque import Base64Encoded


@pytest.fixture(scope="session")
def public_key():
    SCRIPTROOT = Path(__file__).parent.resolve()
    with (SCRIPTROOT / "default.pem").open(encoding="utf-8") as file:
        public_key = RSA.import_key(file.read())
    return public_key


@pytest.fixture(scope="session")
def private_key():
    SCRIPTROOT = Path(__file__).parent.resolve()
    with (SCRIPTROOT / "private.pem").open(encoding="utf-8") as file:
        private_key = RSA.import_key(file.read())
    return private_key


@pytest.fixture()
def encryptedstringdeque(public_key, private_key):
    format_func = partial(EncryptedStringDeque.decrypt, private_key=private_key)
    obj = EncryptedStringDeque(public_key=public_key, sep="\n", format_func=format_func)
    return obj


def test_empty(encryptedstringdeque):
    assert str(encryptedstringdeque) == ""


def test_add(encryptedstringdeque):
    encryptedstringdeque = encryptedstringdeque + "Line 1"
    encryptedstringdeque = encryptedstringdeque + 2
    assert str(encryptedstringdeque) == "Line 1\n2"


def tests_radd(encryptedstringdeque):
    encryptedstringdeque = "Line 1" + encryptedstringdeque
    encryptedstringdeque = 2 + encryptedstringdeque
    assert str(encryptedstringdeque) == "Line 1\n2"


def test_iadd(encryptedstringdeque):
    encryptedstringdeque += "Line 1"
    encryptedstringdeque += 2
    assert str(encryptedstringdeque) == "Line 1\n2"


def test_ror(encryptedstringdeque):
    encryptedstringdeque = ["Line1", "Line2"] | encryptedstringdeque
    encryptedstringdeque = [3, 4] | encryptedstringdeque
    assert str(encryptedstringdeque) == "Line1\nLine2\n3\n4"


def test_len(encryptedstringdeque):
    encryptedstringdeque = encryptedstringdeque + "Line1"
    encryptedstringdeque += 2
    encryptedstringdeque = ["Line3", 4] | encryptedstringdeque
    encryptedstringdeque |= [5, "Line6"]
    assert len(encryptedstringdeque) == 6


def test_getitem(encryptedstringdeque, private_key):
    encryptedstringdeque += "test"
    encryptedstringdeque += 1
    assert (
        encryptedstringdeque.decrypt(
            msg=encryptedstringdeque[0],
            private_key=private_key,
        )
        == "test"
    )
    assert (
        encryptedstringdeque.decrypt(
            msg=encryptedstringdeque[1],
            private_key=private_key,
        )
        == "1"
    )


def test_setitem(encryptedstringdeque, private_key):
    with pytest.raises(IndexError):
        encryptedstringdeque[0] = "test"
    with pytest.raises(IndexError):
        encryptedstringdeque[1] = 1
    encryptedstringdeque += "old"
    assert (
        encryptedstringdeque.decrypt(
            msg=encryptedstringdeque[0],
            private_key=private_key,
        )
        == "old"
    )
    encryptedstringdeque[0] = "new"
    assert (
        encryptedstringdeque.decrypt(
            msg=encryptedstringdeque[0],
            private_key=private_key,
        )
        == "new"
    )


def test_format_funct(public_key):
    encryptedstringdeque = EncryptedStringDeque(public_key=public_key, sep="\n")
    encryptedstringdeque += "test"
    encryptedstringdeque[0]
    enc_session_key = encryptedstringdeque[0].enc_session_key
    nonce = encryptedstringdeque[0].nonce
    tag = encryptedstringdeque[0].tag
    ciphertext = encryptedstringdeque[0].ciphertext
    other = RSAMessage(
        enc_session_key=enc_session_key,
        nonce=nonce,
        tag=tag,
        ciphertext=ciphertext,
    )
    assert encryptedstringdeque[0] == other


def test_str(encryptedstringdeque):
    encryptedstringdeque += "first line"
    encryptedstringdeque = encryptedstringdeque + "line 2"
    encryptedstringdeque = [
        "several more",
        "will be overwritten",
    ] | encryptedstringdeque
    encryptedstringdeque |= ["final"]
    encryptedstringdeque[-2] = "second_to_final_changed"
    assert (
        str(encryptedstringdeque)
        == """\
first line
line 2
several more
second_to_final_changed
final"""
    )


def test_draw(encryptedstringdeque, private_key):
    encryptedstringdeque += "line 1"
    msg = encryptedstringdeque.draw()
    assert type(msg) == RSAMessage
    assert encryptedstringdeque.decrypt(msg=msg, private_key=private_key) == "line 1"


def test_clear(encryptedstringdeque):
    encryptedstringdeque += "line 1"
    encryptedstringdeque += "line 2"
    assert len(encryptedstringdeque) == 2
    assert str(encryptedstringdeque) != ""
    encryptedstringdeque.clear()
    assert len(encryptedstringdeque) == 0
    assert str(encryptedstringdeque) == ""


def test_insert(encryptedstringdeque):
    def conv_func(obj: int) -> str:
        return str(obj * 2)

    encryptedstringdeque.insert([1, 2, 3, 4, 5, 6, 7, 8, 9], conv_func)
    assert (
        str(encryptedstringdeque)
        == """\
2
4
6
8
10
12
14
16
18"""
    )


def test_init_alt_paths(public_key, private_key):
    format_func = partial(EncryptedStringDeque.decrypt, private_key=private_key)
    test = EncryptedStringDeque(
        data="string init test",
        public_key=public_key,
        format_func=format_func,
    )
    assert str(test) == "string init test"


def test_Base64Encoded_error():
    assert Base64Encoded.is_base64("abcdefghia") is False
    assert Base64Encoded.is_base64(base64.b64encode(b"abcdefghia")) is True


def test_Base64Encoded_set_bytes():
    test = RSAMessage(enc_session_key="", nonce="test", tag="", ciphertext="")
    test.ciphertext = "abcdefghia"
    assert test.ciphertext == base64.b64encode(b"abcdefghia").decode()


def test_RSAMessage_required():
    with pytest.raises(TypeError):
        RSAMessage()
