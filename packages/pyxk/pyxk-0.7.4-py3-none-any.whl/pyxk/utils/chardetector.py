"""字符集探测器

from pyxk import chardet, CharDetector

detector = CharDetector()
detector.feed(b"Hello World")
result = detector.close()

# chardet
result = chardet(b"Hello World")

>>>
    CharDetectorResult(
        encoding='ascii',
        confidence=1.0,
        language=''
    )
"""
from typing import Union, Optional

from pyxk.utils import allowed
from pyxk.lazy_loader import LazyLoader
from pyxk.utils.typedef import CharDetectorResult

_chardet = LazyLoader("_chardet", globals(), "chardet")


ByteStr = Union[bytes, bytearray]

__all__ = ["CharDetector", "chardet"]


class CharDetector:
    """字符集探测器

    from pyxk import chardet, CharDetector

    detector = CharDetector()
    detector.feed(b"Hello World")
    result = detector.close()

    # chardet
    result = chardet(b"Hello World")

    >>>
        CharDetectorResult(
            encoding='ascii',
            confidence=1.0,
            language=''
        )
    """
    def __init__(
        self,
        *,
        default_encoding: Optional[str] = None,
        should_rename_legacy: bool = False,
    ):
        """CharDetector初始化 - chardet.UniversalDetector

        :param default_encoding: 字符探测器编码若为None, 则使用default_encoding
        :param should_rename_legacy: should_rename_legacy
        """
        # 类型检测
        self._allowed(
            default_encoding=default_encoding,
            should_rename_legacy=should_rename_legacy,
        )
        # chardet.UniversalDetector
        self.detector = _chardet.UniversalDetector(
            should_rename_legacy=should_rename_legacy,
        )
        # 默认编码
        self._default_encoding = default_encoding

    @classmethod
    def chardet(
        cls,
        byte_str: ByteStr,
        *,
        default_encoding: Optional[str] = None,
        should_rename_legacy: bool = False,
    ) -> CharDetectorResult:
        """提交一个文档，提供给所有相关的字符集探测器，并提出最终预测

        :param byte_str: byte_str
        :param default_encoding: 字符探测器编码若为None, 则使用default_encoding
        :param should_rename_legacy: should_rename_legacy
        :return: CharDetectorResult
        """
        self = cls(
            default_encoding=default_encoding,
            should_rename_legacy=should_rename_legacy,
        )
        self.feed(byte_str)
        return self.close()

    def feed(self, byte_str: ByteStr) -> None:
        """获取文档的一个块，并将其提供给所有相关的字符集探测器

        :param byte_str: byte_str
        """
        self._allowed(byte_str=byte_str)
        self.detector.feed(byte_str)

    @property
    def done(self) -> bool:
        """当前文档分析是否完成"""
        return self.detector.done

    def close(self) -> CharDetectorResult:
        """停止分析当前文档，并提出最终预测"""
        result = self.detector.close().copy()
        if result["encoding"] is None:
            result["encoding"] = self._default_encoding
        return CharDetectorResult(**result)

    def reset(self) -> None:
        """将UniversalDetector及其所有探测器重置为初始状态"""
        return self.detector.reset()

    @property
    def result(self) -> CharDetectorResult:
        """获取文档预测结果，可能不是最终结果"""
        return CharDetectorResult(**self.detector.result)

    @staticmethod
    def _allowed(**kwargs) -> None:
        allowable = {
            "byte_str": (bytes, bytearray),
            "default_encoding": (str, type(None)),
            "should_rename_legacy": (bool,)
        }
        allowed(allowable=allowable, **kwargs)


def chardet(
    byte_str: ByteStr,
    *,
    default_encoding: Optional[str] = None,
    should_rename_legacy: bool = False,
) -> CharDetectorResult:
    """提交一个文档，提供给所有相关的字符集探测器，并提出最终预测

    :param byte_str: byte_str
    :param default_encoding: 字符探测器编码若为None, 则使用default_encoding
    :param should_rename_legacy: should_rename_legacy
    :return: CharDetectorResult
    """
    return CharDetector.chardet(
        byte_str,
        default_encoding=default_encoding,
        should_rename_legacy=should_rename_legacy
    )
