"""AES加解密

from pyxk.cryptor import Crypto, MODES

cipher = Crypto(
    key=b'1234567890123456',
    mode=MODES.CBC,
    iv=b'1234567890123456'
)
raw_text = 'Hello World'
ciphertext = cipher.encrypt(raw_text)
plaintext = cipher.decrypt(ciphertext)

print('raw text:', raw_text)
print('ciphertext:', ciphertext)
print('plaintext:', plaintext)

>>> raw text: Hello World
>>> ciphertext: b'\xf7\x16\x85)|,\x91\x8c\xdbd\xaef\xc3Wbu'
>>> plaintext: b'Hello World'
"""
from typing import Any, Dict, Union, NamedTuple, Optional

from Crypto.Cipher import AES
from pyxk.utils import allowed as _allowed


__all__ = ["Crypto", "encrypt", "decrypt", "Modes"]

class AESMODES(NamedTuple):
    ECB: int
    CBC: int
    CFB: int
    OFB: int
    CTR: int
    OPENPGP: int
    EAX: int
    CCM: int
    SIV: int
    GCM: int
    OCB: int

Modes = AESMODES(
    ECB=1,
    CBC=2,
    CFB=3,
    OFB=5,
    CTR=6,
    OPENPGP=7,
    EAX=9,
    CCM=8,
    SIV=10,
    GCM=11,
    OCB=12
)


class Crypto:
    """AES加解密

    from pyxk.cryptor import Crypto, MODES

    cipher = Crypto(
        key=b'1234567890123456',
        mode=MODES.CBC,
        iv=b'1234567890123456'
    )
    raw_text = 'Hello World'
    ciphertext = cipher.encrypt(raw_text)
    plaintext = cipher.decrypt(ciphertext)

    print('raw text:', raw_text)
    print('ciphertext:', ciphertext)
    print('plaintext:', plaintext)

    >>>
    raw text: Hello World
    ciphertext: b'\xf7\x16\x85)|,\x91\x8c\xdbd\xaef\xc3Wbu'
    plaintext: b'Hello World'
    """
    MODES = Modes

    def __init__(
        self,
        key: Union[str, bytes],
        mode: Union[str, int] = "CBC",
        encoding: str = "utf-8",
        **kwargs: Dict[str, Any]
    ) -> None:
        """Crypto Init

        :param key: 加密/解密 密钥
        :param mode: 加密/解密 模式
        :param encoding: encoding
        :param **kwargs: kwargs
        """
        self.allowed(encoding=encoding)
        self._encoding = encoding
        self._key = self._init_key(key)
        self._mode = self._init_mode(mode)
        self._attrs = kwargs.copy()
        self._padding = b"\x00"
        self._cipher = self.create_cipher()

    def allowed(self, **kwargs: Dict[str, Any]) -> None:
        """初始化"""
        if not kwargs:
            kwargs = {"key": self._key, "mode": self._mode, "encoding": self._encoding}
        allowable = {
            "key": (str, bytes),
            "mode": (int, str),
            "encoding": (str,),
            "plaintext": (str, bytes),
            "ciphertext": (bytes,),
        }
        _allowed(allowable=allowable, **kwargs)

    def encrypt(self, plaintext: Union[str, bytes], new_cipher=True) -> bytes:
        """加密

        :param plaintext: 加密明文
        :param new_cipher: 是否重新创建cipher
        :return: bytes
        """
        self.allowed(plaintext=plaintext)
        if isinstance(plaintext, str):
            plaintext = plaintext.encode(self._encoding)
        # 填充字符
        plaintext = self.padding(plaintext)
        # 加密
        cipher = self.new_cipher if new_cipher else self.cipher
        ciphertext = cipher.encrypt(plaintext)
        return ciphertext

    def decrypt(self, ciphertext: bytes, new_cipher=True) -> bytes:
        """解密

        :param ciphertext: 解密密文
        :param new_cipher: 是否重新创建cipher
        :return: bytes
        """
        self.allowed(ciphertext=ciphertext)
        # 解密
        cipher = self.new_cipher if new_cipher else self.cipher
        plaintext = cipher.decrypt(ciphertext)
        return plaintext.rstrip(self._padding)

    def padding(self, text: bytes, pad: Optional[bytes]=None) -> bytes:
        """填充字符至16倍数

        :param text: 需要填充的数据
        :param pad: 填充字符
        :return: bytes
        """
        _allowed(
            dict( text=(bytes,), pad=(bytes, type(None)) ),
            text=text, pad=pad
        )
        pad = pad if pad else self._padding
        # 填充字符
        remainder = len(text) % AES.block_size or AES.block_size
        text += pad * (AES.block_size - remainder)
        return text

    def _init_key(self, key) -> bytes:
        """初始化密钥 key"""
        self.allowed(key=key)
        if isinstance(key, str):
            key = key.encode(self._encoding)
        # 长度不合法
        if len(key) not in AES.key_size:
            expected = AES.key_size
            raise ValueError(f"'key' length must be in the {expected}. got: {len(key)}")
        return key

    def _init_mode(self, mode) -> int:
        """初始化mode"""
        self.allowed(mode=mode)
        # mode type str
        if isinstance(mode, str):
            mode = mode.upper()
            # 无效mode
            if mode not in self.modes:
                expected = tuple(self.modes.keys())
                raise ValueError(f"'mode' value must be in the {expected}. got: {mode}")
            mode = self.modes[mode]
        # mode type int
        elif mode not in self.modes.values():
            expected = tuple(self.modes.values())
            raise ValueError(f"'mode' value must be in the {expected}. got: {mode}")
        return mode

    def create_cipher(self):
        """创建 AES.cipher"""
        return AES.new(key=self._key, mode=self._mode, **self._attrs)

    @property
    def modes(self) -> dict:
        """all modes"""
        return self.__class__.MODES._asdict()

    @property
    def cipher(self):
        """AES Crypto Cipher"""
        return self._cipher

    @property
    def new_cipher(self):
        """每次调用新建 AES Crypto Cipher"""
        self._cipher = self.create_cipher()
        return self._cipher

    @property
    def key(self):
        """AES Crypto key"""
        return self._key

    @key.setter
    def key(self, value):
        self._key = self._init_key(value)
        self._cipher = self.create_cipher()

    @property
    def mode(self):
        """AES Crypto mode"""
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = self._init_mode(value)
        self._cipher = self.create_cipher()

    @property
    def attrs(self) -> dict:
        """AES Crypto Cipher attributes"""
        return self._attrs

    @attrs.setter
    def attrs(self, value):
        _allowed({"attrs": (dict,)}, attrs=value)
        self._attrs.update(value)
        self._cipher = self.create_cipher()


def encrypt(
    key: Union[str, bytes],
    plaintext: Union[str, bytes],
    mode: Union[str, int] = "CBC",
    **kwargs
) -> bytes:
    """加密

    :param key: 加密密钥
    :param plaintext: 加密明文
    :param mode: 加密模式
    :param kwargs: kwargs
    :return: bytes
    """
    cipher = Crypto(key=key, mode=mode, **kwargs)
    return cipher.encrypt(plaintext, new_cipher=True)


def decrypt(
    key: Union[str, bytes],
    ciphertext: bytes,
    mode: Union[str, int] = "CBC",
    **kwargs
) -> bytes:
    """解密

    :param key: 解密密钥
    :param ciphertext: 解密密文
    :param mode: 解密模式
    :param kwargs: kwargs
    :return: bytes
    """
    cipher = Crypto(key=key, mode=mode, **kwargs)
    return cipher.decrypt(ciphertext, new_cipher=True)
