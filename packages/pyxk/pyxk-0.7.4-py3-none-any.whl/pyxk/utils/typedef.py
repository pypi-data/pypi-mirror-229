from pathlib import Path
from typing import Any, Union, Optional, NamedTuple


__all__ = ["Time", "Number", "Rename", "MD5", "Units"]


class Time(NamedTuple):
    hour: int
    minute: int
    second: int
    positive: Optional[bool]


class Number(NamedTuple):
    number: Optional[Union[int, float]]
    raw: Union[str, int, float]
    is_number: bool


class Rename(NamedTuple):
    rename: Path
    parent: Path
    name: str


class UserAgentNamedTuple(NamedTuple):
    ios: str
    mac: str
    linux: str
    android: str
    windows: str


class MD5(NamedTuple):
    plaintext: Union[bytes, bytearray]
    ciphertext: str


class Units(NamedTuple):
    num: Optional[str]
    raw: Any
    units: str
    string: Optional[str]


class CharDetectorResult(NamedTuple):
    encoding: Optional[str]
    confidence: float
    language: Optional[str]
