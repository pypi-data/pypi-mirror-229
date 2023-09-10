"""Requests session.

from pyxk import requests

session = requests.Session()
session.get("https://httpbin.org/get")

>>> <Response [200]>

Or as a context manager::

with requests.Session() as session:
    session.get("https://httpbin.org/get")

>>> <Response [200]>
"""
from pyxk.request._api import (
    delete,
    get,
    head,
    options,
    patch,
    post,
    put,
    request,
    downloader
)
from pyxk.request._sessions import Session


__all__ = [
    "Session",
    "delete",
    "get",
    "head",
    "options",
    "patch",
    "post",
    "put",
    "request",
    "downloader"
]
