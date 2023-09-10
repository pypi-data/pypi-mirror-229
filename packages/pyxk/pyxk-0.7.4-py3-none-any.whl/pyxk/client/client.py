from types import MethodType
from typing import Any, Type, Union, Dict, Optional

from pyxk.lazy_loader import LazyLoader
from pyxk.utils.main import allowed
from pyxk.client._base import URL, BaseClient
from pyxk.client._typedef import *

parse = LazyLoader("parse", globals(), "urllib.parse")
asyncio = LazyLoader("asyncio", globals(), "asyncio")
aiohttp = LazyLoader("aiohttp", globals(), "aiohttp")
logging = LazyLoader("logging", globals(), "logging")
client_exceptions = LazyLoader("client_exceptions", globals(), "aiohttp.client_exceptions")


__all__ = ["Client", "Response"]


def _add_instance_method(response):
    """为异步response添加实例方法"""
    method_list = set(dir(Response)) - set(dir(aiohttp.ClientResponse))
    for method in method_list:
        setattr(
            response,
            method,
            MethodType(
                getattr(Response, method),
                response
            )
        )


class Client(BaseClient):
    """异步下载器

    explain:
    from pyxk.client import Client, Response

    class Download(Client):
        start_urls = [("http://www.baidu.com", {"title": "百度"})]

        async def parse(self, resp: Response, title: str, **kwargs):
            print(resp.url, title)

    Download.run()

    >> https://m.baidu.com/?from=844b&vit=fps 百度
    """
    async def request(
        self,
        url: Url,
        callback: Optional[CallbackFunc] = None,
        *,
        method: str = "GET",
        cb_kwargs: RequestCbKw = {},
        **kwargs: Dict[str, Any]
    ) -> Union[Response, Any]:
        """异步请求发送以及回调

        :param url: URL
        :param callback: 响应response 回调函数(函数是异步的)
        :param method: 请求方法(default: GET)
        :param cb_kwargs: 传递给回调函数的关键字参数
        :param kwargs: 异步请求 request参数
            params, data, json, cookies, headers,
            skip_auto_headers, auth, allow_redirects,
            max_redirects, compress, chunked, expect100,
            raise_for_status, read_until_eof, proxy, proxy_auth,
            timeout, verify_ssl, fingerprint,
            ssl_context, ssl, proxy_headers,
            trace_request_ctx, read_bufsize
        :return: Response, Any
        """
        allowed(
            {"url": (str, URL), "method": (str,), "cb_kwargs": (dict,)},
            url=url, method=method, cb_kwargs=cb_kwargs
        )
        url, method = self.build_url(url), method.upper()

        async with self.semaphore:
            response = await self._request(
                url=url,
                callback=callback,
                method=method,
                cb_kwargs=cb_kwargs,
                **kwargs
            )
        return response

    async def _request(
        self,
        url: Url,
        callback: Optional[CallbackFunc] = None,
        *,
        method: str = "GET",
        cb_kwargs: RequestCbKw = {},
        **kwargs: Dict[str, Any]
    ) -> Union[Response, Any]:
        """发送单个异步Http/Https请求 以及 响应回调"""
        # request警告消息开关
        switch = {
            key: self.warning
            for key in ("retry", "succeed", "timeout", "client", "disconnected")
        }
        switch.update({"url": url, "method": method})

        # request 最大重试次数
        resp_ret = ResponseResult()
        for _ in range(self.max_retries):
            try:
                resp_ret = await self._send(
                    method=method, url=url, switch=switch, **kwargs
                )
                # 请求未成功
                if not resp_ret.completed:
                    continue

                # 为response添加实例方法
                _add_instance_method(resp_ret.response)

                # 开启回调函数
                if callable(callback):
                    result = await callback(resp_ret.response, **cb_kwargs)
                else:
                    result = resp_ret.response

                break
            # 请求超时 重试
            except asyncio.exceptions.TimeoutError as e:
                resp_ret = ResponseResult(error=e)
                await self._warning("timeout", switch)

            # 连接错误 重试
            except (
                client_exceptions.ClientOSError,
                client_exceptions.ClientPayloadError,
                client_exceptions.ClientConnectorError
            ) as e:
                resp_ret = ResponseResult(error=e)
                await self._warning("client", switch)

            # 服务器拒绝连接
            except client_exceptions.ServerDisconnectedError as e:
                resp_ret = ResponseResult(error=e)
                await self._warning("disconnected", switch)

            # 关闭 response
            finally:
                if resp_ret.response and callable(callback):
                    resp_ret.response.close()

        # 达到最大重试次数
        else:
            if resp_ret.error:
                raise resp_ret.error
            raise RuntimeError(
                f"<{method} {url}>: exceeded max_retries: {self.max_retries}."
                f"\nstatus_retry_list: {self.status_retry_list}."
                f"\nstatus_error_list: {self.status_error_list}."
                f"\nuntil_request_succeed: {self.until_request_succeed}."
            )
        return result

    async def _send(
        self,
        method: str,
        url: Url,
        *,
        switch: Optional[dict] = None,
        **kwargs: Dict[str, Any]
    ) -> ResponseResult:
        """调用 aiohttp.ClientSession 发送异步请求"""
        allowed({"switch": (dict, type(None))}, switch=switch)
        switch = {} if switch is None else switch

        response = await self.session.request(method=method, url=url, **kwargs)
        # 解析response状态码
        retry = self.status_retry_list.copy()
        error = self.status_error_list.copy()
        succeed = [200] if self.until_request_succeed is True else self.until_request_succeed

        # until_request_succeed
        if self.until_request_succeed:
            if response.status in succeed:
                return ResponseResult(response, True)

            retry, error, succeed = [response.status], [], None
            await self._warning("succeed", switch, response)
        # error
        if response.status in error:
            raise RuntimeError(
                f"{response.status}: {response.url.human_repr()!r}"
                f" in the status_error_list: {self.status_error_list}"
            )
        # retry
        if response.status in retry:
            if succeed is not None:
                await self._warning("retry", switch, response)
            return ResponseResult(response, False)
        # 成功
        return ResponseResult(response, True)

    async def _warning(
        self, key: str,
        switch: dict,
        response: Optional[Response] = None
    ) -> None:
        """request 警告消息"""
        warn = {
            "retry": lambda r: f"Retry: {r.status}: <{r.method} {r.url.human_repr()}>"
                     f". expected: {self.status_retry_list}",
            "succeed": lambda r: f"UntilRequestSucceed: {r.status}: <{r.method} {r.url.human_repr()}>"
                       f". expected: {self.until_request_succeed}",
            "timeout": lambda r: f"Timeout: <{switch['method']} {switch['url']}>",
            "client": lambda r: f"ClientError: <{switch['method']} {switch['url']}>",
            "disconnected": lambda r: f"Disconnected: <{switch['method']} {switch['url']}>"
        }
        # 无效key
        if key not in warn:
            raise ValueError(f"{key!r} not in dict. expected: {list(warn)}")
        if switch[key]:
            # 发出警告
            message = warn[key](response)
            logging.warning(message)
            # 确保只会发出一次警告
            switch[key] = False
        await self.sleep()

    async def gather(
        self,
        urls: Urls,
        callback: Optional[CallbackFunc] = None,
        *,
        method: str = "GET",
        cb_kwargs: Optional[RequestCbKwList] = None,
        return_exceptions: bool = False,
        auto_set_base_url: Union[str, URL, bool, None] = False,
        **kwargs: Dict[str, Any]
    ):
        """发送url列表，创建异步任务 并发发送

        :param urls: Url List
        :param callback: 响应response 回调函数(函数是异步的)
        :param method: 请求方法(default: GET)
        :param cb_kwargs: 回调函数关键字参数列表
        :param return_exceptions: 错误传递(default: False)
        :param auto_set_base_url: 是否设置base_url
        :return: list
        """
        allowed(
            allowable={
                "urls": (list,),
                "method": (str,),
                "cb_kwargs": (dict, list, type(None)),
                "auto_set_base_url": (str, URL, bool, type(None))
            },
            urls=urls, method=method, cb_kwargs=cb_kwargs, auto_set_base_url=auto_set_base_url
        )

        # cb_kwargs
        if not cb_kwargs:
            cb_kwargs = {}
        cb_kwargs = self._parse_gather_cb_kwargs(cb_kwargs, len(urls))

        # urls
        if not all((x and isinstance(x, (URL, str, tuple, list)) for x in urls)):
            raise ValueError(
                f"'urls' invalid. got: {urls}\n"
                "expected: [ 'https://xxx', ... ] or [ ('https://xxx', {'index': 0}), ... ]"
            )

        for index, item in enumerate(urls):
            # 直接连接
            if isinstance(item, (str, URL)):
                continue
            # 带有参数
            if len(item) >= 2:
                urls[index] = item[0]
                kw = item[1]
                kw.update(cb_kwargs[index])
                cb_kwargs[index] = kw
            elif len(item) == 1:
                urls[index] = item[0]

        # 设置 base url
        if auto_set_base_url:
            if auto_set_base_url is True:
                self.base_url = parse.urljoin(str(urls[0]), ".")
            else:
                self.base_url = auto_set_base_url
        elif auto_set_base_url is None:
            self.base_url = None

        # 开启一组异步任务
        request_tasks = [
            self.request(url, callback, method=method, cb_kwargs=kw, **kwargs)
            for url, kw in zip(urls, cb_kwargs)
        ]
        return await asyncio.gather(*request_tasks, return_exceptions=return_exceptions)

    @staticmethod
    def _parse_gather_cb_kwargs(cb_kwargs: Union[list, dict], length: int) -> list:
        """解析 gather-cb_kwargs"""
        # cb_kwargs类型为字典
        if isinstance(cb_kwargs, dict):
            return [cb_kwargs.copy() for _ in range(length)]
        if not isinstance(cb_kwargs, list):
            raise Type(f"'gather.cb_kwargs' type must be a list or dict, got: {type(cb_kwargs)}")

        # cb_kwargs类型为列表
        cb_kwargs = cb_kwargs[:length]
        # cb_kwargs每一项必须为字典
        if not all( map(lambda x: isinstance(x, dict), cb_kwargs) ):
            raise ValueError("'cb_kwargs' each value must be a dict.")
        if len(cb_kwargs) < length:
            cb_kwargs.extend([{} for _ in range(length-len(cb_kwargs))])

        return cb_kwargs

    async def start_request(
        self,
        urls: Optional[Urls] = None,
        callback: Optional[CallbackFunc] = None,
        *,
        method: str = "GET",
        cb_kwargs: Optional[RequestCbKwList] = None,
        return_exceptions: bool = False,
        auto_set_base_url: Union[str, URL, bool, None] = True,
        completed: Optional[FuncCbKw] = None,
        callback_of_completed: Optional[CallbackFunc] = None,
        **kwargs: Dict[str, Any]
    ):
        """默认请求方法

        :param urls: Url List
        :param callback: 响应response 回调函数(函数是异步的)
        :param method: 请求方法(default: GET)
        :param cb_kwargs: 回调函数关键字参数列表
        :param return_exceptions: 错误传递(default: False)
        :param auto_set_base_url: 是否设置base_url
        :param completed: 回调函数参数(dict)
        :param callback_of_completed: 回调函数
        """
        await self._start_request(
            urls=urls,
            callback=callback,
            method=method,
            cb_kwargs=cb_kwargs,
            return_exceptions=return_exceptions,
            auto_set_base_url=auto_set_base_url,
            completed=completed,
            callback_of_completed=callback_of_completed,
            **kwargs
        )

    async def _start_request(
        self,
        urls: Optional[Urls] = None,
        callback: Optional[CallbackFunc] = None,
        method: str = "GET",
        cb_kwargs: Optional[RequestCbKwList] = None,
        return_exceptions: bool = False,
        auto_set_base_url: Union[str, URL, bool, None] = True,
        completed: Optional[FuncCbKw] = None,
        callback_of_completed: Optional[CallbackFunc] = None,
        **kwargs: Dict[str, Any]
    ):
        """默认请求方法"""
        allowed(
            {"urls": (list, type(None)), "completed": (dict, type(None))},
            urls=urls, completed=completed,
        )
        # completed
        completed = {} if completed is None else completed
        # start_urls
        start_urls = urls if urls else self.start_urls.copy()
        # 无效urls
        if not isinstance(start_urls, list):
            raise NotImplementedError(f"'{self.__class__.__name__}.start_urls' not implemented. got: {self.start_urls}")
        # 空start_urls
        if not start_urls:
            start_request_result = []
        else:
            # 开启异步请求
            kwargs.update(self.request_kw)
            start_request_result = await self.gather(
                start_urls,
                callback if callable(callback) else self.parse,
                method=method,
                cb_kwargs=cb_kwargs,
                return_exceptions=return_exceptions,
                auto_set_base_url=auto_set_base_url,
                **kwargs
            )
        # 回调函数
        if not callable(callback_of_completed):
            callback_of_completed = self.completed
        await callback_of_completed(start_request_result, **completed)

    async def parse(self, response: Response, **kwargs):
        """start_request的默认回调函数"""
        raise NotImplementedError(
            f"'{self.__class__.__name__}.parse' not implemented;"
            " Note: the method is asynchronous."
        )
