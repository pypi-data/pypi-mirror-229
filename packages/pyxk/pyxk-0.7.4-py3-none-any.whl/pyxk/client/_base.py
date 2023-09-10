import asyncio
from multidict import CIMultiDict
from typing import Any, Union, Dict, Optional

from yarl import URL
from aiohttp import TCPConnector, ClientTimeout, ClientSession

from pyxk.utils import user_agents, allowed as _allowed
from pyxk.client._typedef import *


__all__ = ["BaseClient"]


class BaseClient:
    """ClientSession基类"""

    allowable: Allowable = {}
    limit: Limit = 100
    delay: Delay = 1
    verify: bool = True
    warning: bool = True
    timeout: Timeout = 10
    headers: Headers = {}
    semaphore: Semaphore = 16
    user_agent: UserAgent = user_agents.android
    session_kw: SessionKw = {}
    request_kw: RequestKw = {}
    start_urls: Urls = []
    max_retries: int = 10
    status_retry_list: Retry = []
    status_error_list: Error = []
    until_request_succeed: RequestSucceed = False

    __attrs__ = frozenset(
        (
            "limit",
            "delay",
            "verify",
            "warning",
            "timeout",
            "headers",
            "semaphore",
            "user_agent",
            "request_kw",
            "session_kw",
            "start_urls",
            "max_retries",
            "status_retry_list",
            "status_error_list",
            "until_request_succeed",
        )
    )

    def __init__(
        self,
        *,
        loop: Optional[EventLoop] = None,
        base_url: Optional[Url] = None,
        **kwargs
    ) -> None:
        # event loop
        loop = loop or asyncio.get_event_loop()

        # 检查 关键字参数 数据类型
        attrs = { key: getattr(self, key) for key in self.__class__.__attrs__ }
        attrs.update(kwargs)
        attrs["loop"] = loop
        self.allowed(**attrs)

        # 实例化参数
        for key, value in kwargs.items():
            setattr(self, key, value)

        self._loop: EventLoop = loop
        asyncio.set_event_loop(loop)

        self._session: Session = None
        self._base_url: Optional[Url] = self._set_base_url(base_url)

    def allowed(self, allowable: Optional[Allowable] = None, **kwargs) -> None:
        """检查数据类型合法性

        :param allowable: 添加额外的类型检测
        :param **kwargs: 被检测的数据
        """
        if not kwargs:
            kwargs = { key: getattr(self, key) for key in self.__class__.__attrs__ }

        base_allowable = {
            "loop": (asyncio.AbstractEventLoop,),
            "limit": (int,),
            "delay": (int, float),
            "verify": (bool,),
            "warning": (bool,),
            "timeout": (int, float, ClientTimeout),
            "headers": (dict, CIMultiDict, type(None)),
            "semaphore": (int, asyncio.Semaphore),
            "user_agent": (str, type(None)),
            "request_kw": (dict,),
            "session_kw": (dict,),
            "start_urls": (list,),
            "max_retries": (int,),
            "status_retry_list": (list,),
            "status_error_list": (list,),
            "until_request_succeed": (list, bool),
        }

        # 额外可允许的类型
        if not isinstance(self.allowable, dict):
            raise TypeError(f"'{self.__class__.__name__}.allowable' type must be a dict. got: {type(self.allowable)}")

        if not isinstance(allowable, dict):
            if allowable is not None:
                raise TypeError(f"'allowable' type must be a dict. got: {type(allowable)}")
            allowable = {}

        # 全部类型
        base_allowable.update(self.allowable)
        base_allowable.update(allowable)
        # 检测数据类型
        _allowed(allowable=base_allowable, callback=self._cb_allowed, **kwargs)

    @staticmethod
    def _cb_allowed(key: str, value: Any) -> None:
        """检查数据值域"""
        message = lambda x: f"{key!r} initial value must be {x}. got: {value}"
        status_message = f"{key!r} all value types must be int. got: {value}"
        allowable = {
            "limit": ((int,), lambda x: x>0, message("> 0")),
            "delay": ((int, float), lambda x: x>=0, message(">= 0")),
            "semaphore": ((int,), lambda x: x>0, message("> 0")),
            "max_retries": ((int,), lambda x: x>0, message("> 0")),
            "timeout": ((int, float), lambda x: x>0, message("> 0")),
            "status_retry_list": ((list,), lambda x: all(isinstance(i, int) for i in x), status_message),
            "status_error_list": ((list,), lambda x: all(isinstance(i, int) for i in x), status_message),
            "until_request_succeed": ((list,), lambda x: all(isinstance(i, int) for i in x), status_message),
        }
        # 不为检查对象
        if (
            key not in allowable
            or not isinstance(value, allowable[key][0])
        ):
            return
        # 检查不在值域的数据
        if not allowable[key][1](value):
            raise ValueError(allowable[key][2])

    @staticmethod
    def _set_base_url(url: Url) -> Optional[Url]:
        """解析 base_url"""
        if not isinstance(url, (str, URL)):
            if url is None:
                return None
            raise TypeError(f"'base_url' type must be a 'str' or 'yarl.URL', got: {type(url)}")
        url = URL(url)
        if url.is_absolute():
            return url
        return None

    @property
    def loop(self) -> EventLoop:
        """asyncio.AbstractEventLoop"""
        return self._loop

    @property
    def session(self) -> Session:
        """aiohttp.ClientSession"""
        return self._session

    @property
    def base_url(self) -> Optional[Url]:
        """yarl.URL(base_url)"""
        return self._base_url

    @base_url.setter
    def base_url(self, _url: Url) -> None:
        self._base_url = self._set_base_url(_url)

    @property
    def _func_allowable(self) -> None:
        """部分方法参数类型检测"""
        return {
            x: (dict, type(None))
            for x in ("open", "start", "start_request", "stop", "close", "completed")
        }

    @classmethod
    def run(
        cls,
        *,
        base_url: Optional[Url] = None,
        open: FuncCbKw = None,
        start: FuncCbKw = None,
        start_request: FuncCbKw = None,
        stop: FuncCbKw = None,
        close: FuncCbKw = None,
        completed: FuncCbKw = None,
        **kwargs: Dict[str, Any]
    ):
        """程序运行入口 - 应该调用该方法运行

        :param base_url: base url
        :param open: self.open 参数
        :param start: self.start 参数
        :param start_request: self.start_request 参数
        :param stop: self.stop 参数
        :param close: self.close 参数
        :param completed: self.completed 参数
        """
        kwargs.update( {"loop": asyncio.new_event_loop()} )
        self = cls(base_url=base_url, **kwargs)

        # 检查参数类型
        self.allowed(
            self._func_allowable,
            open=open,
            start=start,
            start_request=start_request,
            stop=stop,
            close=close,
            completed=completed
        )

        # 开启 event loop, 并启动 ClientSession
        self.run_with_event_loop(
            open=open or {},
            start=start or {},
            start_request=start_request or {},
            stop=stop or {},
            close=close or {},
            completed=completed or {},
        )

        # 关闭 event loop
        if self.loop:
            self.loop.close()
            asyncio.set_event_loop(None)
        return self

    async def main(
        self,
        *,
        open: FuncCbKw = None,
        start: FuncCbKw = None,
        start_request: FuncCbKw = None,
        stop: FuncCbKw = None,
        close: FuncCbKw = None,
        completed: FuncCbKw = None,
    ) -> None:
        """从此方法开启异步连接器生命周期

        :param open: self.open 参数
        :param start: self.start 参数
        :param start_request: self.start_request 参数
        :param stop: self.stop 参数
        :param close: self.close 参数
        :param completed: self.completed 参数
        """
        # 检查参数类型
        self.allowed(
            self._func_allowable,
            open=open,
            start=start,
            start_request=start_request,
            stop=stop,
            close=close,
            completed=completed,
            **{ x: getattr(self, x) for x in self.__class__.__attrs__ }
        )

        try:
            await self.open(**open or {})
            await self._main(
                start=start or {},
                start_request=start_request or {},
                stop=stop or {},
                completed=completed or {},
            )
        finally:
            await self.close(**close or {})

    async def _main(
        self,
        *,
        start: FuncCbKw = None,
        start_request: FuncCbKw = None,
        stop: FuncCbKw = None,
        completed: FuncCbKw = None,
    ) -> None:
        """从此方法开启异步连接器生命周期

        :param start: self.start 参数
        :param start_request: self.start_request 参数
        :param stop: self.stop 参数
        :param completed: self.completed 参数
        """
        # semaphore
        if not isinstance(self.semaphore, asyncio.Semaphore):
            self.semaphore = asyncio.Semaphore(self.semaphore)

        # aiohttp timeout(超时时间)
        if not isinstance(self.timeout, ClientTimeout):
            self.timeout: Timeout = ClientTimeout(total=self.timeout)

        # aiohttp connector(连接器)
        connector = TCPConnector(limit=self.limit, ssl=self.verify, loop=self.loop)

        # aiohttp headers
        self.headers: Headers = CIMultiDict(self.headers or {})
        # -- headers.user_agent
        if self.user_agent:
            self.headers["User-Agent"] = self.user_agent
        self.headers.setdefault("User-Agent", user_agents.android)

        try:
            # 创建 aiohttp.ClientSession
            self._session: Session = ClientSession(
                loop=self.loop,
                connector=connector,
                timeout=self.timeout,
                headers=self.headers,
                **self.session_kw
            )

            # start
            await self.start(**start or {})
            # start_request
            if completed:
                start_request.update( {"completed": completed} )
            await self.start_request(**start_request)

        finally:
            # stop
            await self.stop(**stop)
            # 关闭 ClientSession
            if self._session:
                await self._session.close()

    def run_with_event_loop(
        self,
        *,
        open: FuncCbKw = None,
        start: FuncCbKw = None,
        start_request: FuncCbKw = None,
        stop: FuncCbKw = None,
        close: FuncCbKw = None,
        completed: FuncCbKw = None,
    ) -> None:
        """使用事件循环运行异步连接器

        :param open: self.open 参数
        :param start: self.start 参数
        :param start_request: self.start_request 参数
        :param stop: self.stop 参数
        :param close: self.close 参数
        :param completed: self.completed 参数
        """
        # 检查参数类型
        self.allowed(
            self._func_allowable,
            open=open,
            start=start,
            start_request=start_request,
            stop=stop,
            close=close,
            completed=completed
        )

        return self.loop.run_until_complete(
            self.main(
                open=open or {},
                start=start or {},
                start_request=start_request or {},
                stop=stop or {},
                close=close or {},
                completed=completed or {}
            )
        )

    async def sleep(
        self,
        delay: Optional[Union[int, float]] = None,
        default: Any = None,
    ) -> Any:
        """异步休眠"""
        delay = self.delay if delay is None else delay
        self.allowed(delay=delay)
        return await asyncio.sleep(delay, default)

    def build_url(self, url: Url) -> Url:
        """构建绝对url路径"""
        self.allowed({"url": (str, URL)}, url=url)
        url = URL(url)
        if (
            not self.base_url
            or url.is_absolute()
        ):
            return url
        return self.base_url.join(url)

    async def start_request(self, *args, **kwargs):
        """开启 CientSession 后默认调用 start_request"""
        raise NotImplementedError(f"'{self.__class__.__name__}.start_request' not implemented")

    async def completed(self, result: list, **kwargs) -> None:
        """start_request 运行完成结果回调函数"""

    async def open(self, **kwargs) -> None:
        """创建 ClientSession 之前调用"""

    async def close(self, **kwargs) -> None:
        """关闭 ClientSession 之后调用"""

    async def start(self, **kwargs) -> None:
        """创建 ClientSession 之后调用"""

    async def stop(self, **kwargs) -> None:
        """关闭 ClientSession 之前调用"""
