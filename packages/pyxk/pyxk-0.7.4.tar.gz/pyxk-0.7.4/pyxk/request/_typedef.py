from typing import (
    Any,
    Dict,
    List,
    Tuple,
    Union,
    Optional,
    Callable,
    NamedTuple,
    MutableMapping,
)

from requests.auth import HTTPBasicAuth
from requests.cookies import RequestsCookieJar
from requests.models import Response
from requests.structures import CaseInsensitiveDict


__all__ = [
    "Response",
    "Url",
    "Method",
    "Params",
    "Auth",
    "Cert",
    "Json",
    "Hooks",
    "Files",
    "Headers",
    "Cookies",
    "Proxies",
    "Data",
    "ResponseResult",
]


Url = str
Method = str
Params = Union[Dict[str, str], MutableMapping[str, str]]
Auth = Union[HTTPBasicAuth, Tuple[Union[str, str]]]
Cert = Optional[Tuple[Union[str, str]]]
Json = Union[Dict[str, Any], MutableMapping[str, Any]]
Hooks = Optional[Dict[str, List[Callable]]]
Files = Union[Dict[str, Any], MutableMapping[str, Any]]
Headers = Union[Dict[str, str], CaseInsensitiveDict]
Cookies = Union[dict, RequestsCookieJar]
Proxies = Optional[Dict[str, str]]
Data = Union[str, bytes, MutableMapping[str, Any]]


class ResponseResult(NamedTuple):
    response: Response = None
    completed: bool = False
    error: Exception = None
