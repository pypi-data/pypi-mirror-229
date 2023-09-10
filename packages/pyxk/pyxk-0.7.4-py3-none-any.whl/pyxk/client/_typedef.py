import typing
import asyncio
from multidict import CIMultiDict

from yarl import URL
from aiohttp import ClientTimeout, ClientResponse, ClientSession
from parsel.selector import Selector, SelectorList

from pyxk.utils import chardet


__all__ = [
    "Url",
    "Urls",
    "Retry",
    "Error",
    "Limit",
    "Delay",
    "Timeout",
    "Session",
    "Allowable",
    "Headers",
    "Response",
    "FuncCbKw",
    "Semaphore",
    "UserAgent",
    "EventLoop",
    "SessionKw",
    "RequestKw",
    "RequestCbKw",
    "CallbackFunc",
    "RequestSucceed",
    "RequestCbKwList",
    "ResponseResult",
]


Url = typing.Union[str, URL]
Urls = typing.Union[
    typing.List[Url],
    typing.List[typing.Union[Url, typing.Dict[str, typing.Any]]]
]
Retry = typing.List[int]
Error = typing.List[int]
Limit = int
Delay = typing.Union[int, float]
Timeout = typing.Union[int, float, ClientTimeout]
Session = ClientSession
Allowable = typing.Dict[str, typing.Tuple[typing.Type]]
Headers = typing.Union[typing.Dict[str, typing.Any], CIMultiDict]
# Response = ClientResponse
FuncCbKw = typing.Optional[typing.Dict[str, typing.Any]]
Semaphore = typing.Union[int, asyncio.Semaphore]
UserAgent = str
EventLoop = asyncio.AbstractEventLoop
SessionKw = typing.Dict[str, typing.Any]
RequestKw = typing.Dict[str, typing.Any]
RequestCbKw = typing.Dict[str, typing.Any]
CallbackFunc = typing.Callable[[ClientResponse], typing.Any]
RequestSucceed = typing.Union[bool, typing.List[int]]
RequestCbKwList = typing.Union[RequestCbKw, typing.List[RequestCbKw]]


class Response(ClientResponse):

    async def _initi_text(self, encoding: typing.Optional[str] = None) -> typing.Tuple[str, str]:
        """解析 text & encoding"""
        try:
            encoding = encoding or self.get_encoding()
            text = await self.text(encoding)
        except UnicodeError:
            text = await self.read()
            encoding = chardet(text).encoding or "utf-8"
            text = text.decode(encoding, errors="ignore")
        return text, encoding

    async def xpath(
        self,
        query: str,
        type: typing.Optional[str] = None,
        encoding: typing.Optional[str] = None,
        base_url: typing.Optional[str] = None,
        namespaces: typing.Optional[typing.Mapping[str, str]] = None,
    ) -> SelectorList[Selector]:
        """selector.xpath

        :param query: xpath查询字符串
        :param type: 文件类型 - "html"(default), "json", or "xml"
        :param encoding: text encoding
        :param base_url: 为文档设置URL
        :param namespaces: `namespaces` is an optional `prefix: namespace-uri` mapping (dict)
            for additional prefixes to those registered with `register_namespace(prefix, uri)`.
            Contrary to `register_namespace()`, these prefixes are not
            saved for future calls.
        """
        text, encoding = await self._initi_text(encoding)
        # selector
        sel = Selector(
            text=text,
            type=type,
            base_url=base_url,
            encoding=encoding,
            namespaces=namespaces
        )
        # xpath
        return sel.xpath(query=query)

    async def css(
        self,
        query: str,
        type: typing.Optional[str] = None,
        encoding: typing.Optional[str] = None,
        base_url: typing.Optional[str] = None,
        namespaces: typing.Optional[typing.Mapping[str, str]] = None,
    ) -> SelectorList[Selector]:
        """selector.css

        :param query: xpath查询字符串
        :param type: 文件类型 - "html"(default), "json", or "xml"
        :param encoding: text encoding
        :param base_url: 为文档设置URL
        :param namespaces:
            `namespaces` is an optional `prefix: namespace-uri` mapping (dict)
            for additional prefixes to those registered with `register_namespace(prefix, uri)`.
            Contrary to `register_namespace()`, these prefixes are not
            saved for future calls.
        """
        text, encoding = await self._initi_text(encoding)
        # selector
        sel = Selector(
            text=text,
            type=type,
            base_url=base_url,
            encoding=encoding,
            namespaces=namespaces
        )
        # css
        return sel.css(query=query)

    async def re(
        self,
        regex: str,
        type: typing.Optional[str] = None,
        encoding: typing.Optional[str] = None,
        base_url: typing.Optional[str] = None,
        namespaces: typing.Optional[typing.Mapping[str, str]] = None,
        replace_entities: bool = True,
    ) -> typing.List[str]:
        """selector.re

        :param regex: 编译的正则表达式 或者 字符串
        :param type: 文件类型 - "html"(default), "json", or "xml"
        :param encoding: text encoding
        :param base_url: 为文档设置URL
        :param namespaces:
            `namespaces` is an optional `prefix: namespace-uri` mapping (dict)
            for additional prefixes to those registered with `register_namespace(prefix, uri)`.
            Contrary to `register_namespace()`, these prefixes are not
            saved for future calls.
        :param replace_entities:
            By default, character entity references are replaced by their
            corresponding character (except for ``&amp;`` and ``&lt;``).
            Passing ``replace_entities`` as ``False`` switches off these
            replacements.
        """
        text, encoding = await self._initi_text(encoding)
        # selector
        sel = Selector(
            text=text,
            type=type,
            base_url=base_url,
            encoding=encoding,
            namespaces=namespaces
        )
        # re
        return sel.re(regex=regex, replace_entities=replace_entities)

    async def selector(
        self,
        type: typing.Optional[str] = None,
        encoding: typing.Optional[str] = None,
        base_url: typing.Optional[str] = None,
        namespaces: typing.Optional[typing.Mapping[str, str]] = None,
        **kwargs
    ) -> Selector:
        """selector

        :param regex: 编译的正则表达式 或者 字符串
        :param type: 文件类型 - "html"(default), "json", or "xml"
        :param encoding: text encoding
        :param base_url: 为文档设置URL
        :param namespaces:
            `namespaces` is an optional `prefix: namespace-uri` mapping (dict)
            for additional prefixes to those registered with `register_namespace(prefix, uri)`.
            Contrary to `register_namespace()`, these prefixes are not
            saved for future calls.
        """
        text, encoding = await self._initi_text(encoding)
        return Selector(
            text=text,
            type=type,
            base_url=base_url,
            encoding=encoding,
            namespaces=namespaces,
            **kwargs
        )

    def urljoin(self, url: Url, **kw) -> Url:
        """yarl.URL - urljoin"""
        if not isinstance(url, (str, URL)):
            raise TypeError(f"'url' must be a str or URL, got: {type(url)}")
        url = URL(url, **kw)
        if url.is_absolute():
            return url
        return self.url.join(url)


class ResponseResult(typing.NamedTuple):
    response: typing.Optional[Response] = None
    completed: bool = False
    error: typing.Optional[Exception] = None
