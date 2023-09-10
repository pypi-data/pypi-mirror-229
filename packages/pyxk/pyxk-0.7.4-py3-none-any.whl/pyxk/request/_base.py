from typing import Union, Optional, List

from requests import Session

from pyxk.utils import user_agents
from pyxk.lazy_loader import LazyLoader
from pyxk.request._typedef import *
from pyxk.request._typedef import CaseInsensitiveDict as CIDict

copy = LazyLoader("copy", globals(), "copy")
parse = LazyLoader("parse", globals(), "urllib.parse")
console = LazyLoader("console", globals(), "rich.console")
exceptions = LazyLoader("exceptions", globals(), "requests.exceptions")


class BaseSession(Session):

    def __init__(
        self,
        *,
        verify: bool = True,
        headers: Optional[Headers] = None,
        base_url: Optional[Url] = None,
        user_agent: Optional[str] = None,
    ):
        super().__init__()

        # 初始化
        self.verify = bool(verify)

        # headers
        headers = CIDict(headers)

        # user_agent
        if not isinstance(user_agent, str):
            if user_agent is not None:
                raise TypeError(f"'user_agent' type must be a str, got: {type(user_agent)}")
        else:
            headers["User-Agent"] = user_agent

        # update headers
        headers.setdefault("User-Agent", user_agents.android)
        self.headers.update(headers)

        # base_url
        self._base_url = self._parse_base_url(base_url)

        # rich.console
        self._console = console.Console()

    def request(
        self,
        method: Method,
        url: Url,
        *,
        params: Params = None,
        data: Data = None,
        headers: Headers = None,
        cookies: Cookies = None,
        files: Files = None,
        auth: Auth = None,
        timeout: Optional[Union[int, float]] = 5,
        allow_redirects: bool = True,
        proxies: Proxies = None,
        hooks: Hooks = None,
        stream: Optional[bool] = None,
        verify: Optional[Union[bool, str]] = None,
        cert: Cert = None,
        json: Json = None,
        max_retries: int = 10,
        loading_status: bool = True,
        status_retry_list: List[int] = [],
        status_error_list: List[int] = [],
        until_request_succeed: Union[bool, List[int]] = False,
    ) -> Response:
        """request(method, url, **kwargs)

        :param method: 'GET', 'POST', 'HEAD', 'OPTIONS', 'DELETE', 'PUT', 'PATCH'
        :param url: url
        :param params: params
        :param data: data
        :param headers: 请求头
        :param cookies: cookies
        :param files: files
        :param auth: auth
        :param timeout: 超时时间
        :param allow_redirects: 请求重定向
        :param proxies: 请求代理
        :param hooks: hooks - {'response': [callable, ...]}
        :param stream: 流式相应 大文件请求
        :param verify: verify ssl
        :param cert: 请求证书
        :param json: jsonm
        :param max_retries: 最大重试次数
        :param loading_status: 请求显示 rich.status
        :param status_retry_list: 状态码重试列表
        :param status_error_list: 状态码错误列表
        :param until_request_succeed: 直到请求成功
        :return: requests.Response
        """
        if not isinstance(method, str):
            raise TypeError(f"'method' type must be a str, got: {type(method)}")

        url, method = self.build_url(url), method.upper()
        # 初始化参数
        until_request_succeed = self._initialization(
            max_retries, status_retry_list, status_error_list, until_request_succeed
        )

        request = {
            "params": params,
            "data": data,
            "headers": headers,
            "cookies": cookies,
            "files": files,
            "auth": auth,
            "timeout": timeout,
            "allow_redirects": allow_redirects,
            "proxies": proxies,
            "hooks": hooks,
            "stream": stream,
            "verify": verify,
            "cert": cert,
            "json": json,
        }

        for index in range(max_retries):
            ret = self._send_req(
                method=method,
                url=url,
                index=f"[{index+1}]" if index else "",
                loading_status=loading_status,
                status_retry_list=status_retry_list.copy(),
                status_error_list=status_error_list.copy(),
                until_request_succeed=until_request_succeed,
                **request
            )
            # 请求成功
            if ret.completed:
                break
        else:
            if ret.error:
                raise ret.error
            raise RuntimeError(
                f"exceeded max retries {max_retries}, "
                f"got: [{ret.response.status_code}]: <{method} {url}>"
            )
        return ret.response

    def _send_req(
        self,
        method: Method,
        url: Url,
        *,
        index: str,
        loading_status: bool,
        status_retry_list: List[int],
        status_error_list: List[int],
        until_request_succeed: List[int],
        **kwargs
    ) -> ResponseResult:
        """发送request请求"""
        # rich.status
        status = self.console.status(f"Request{index}: <[magenta]{method}[/] [bright_blue u]{url}[/]>", spinner="arc")
        if loading_status:
            status.start()

        # 开始请求
        try:
            response = super().request(method=method, url=url, **kwargs)

            # until_request_succeed
            if until_request_succeed:
                if response.status_code in until_request_succeed:
                    return ResponseResult(response, True)
                status_retry_list, status_error_list = [response.status_code], []

            # status_error_list
            if response.status_code in status_error_list:
                raise exceptions.RequestException(
                    f"{response.status_code}: <{method} {url}> in the 'status_error_list': {status_error_list}"
                )
            # status_retry_list
            if response.status_code in status_retry_list:
                return ResponseResult(response, False)
        except (
            exceptions.Timeout,
            exceptions.ConnectionError,
            exceptions.ChunkedEncodingError,
        ) as error:
            return ResponseResult(error=error)
        finally:
            # 关闭rich.status
            status.stop()

        return ResponseResult(response, True)

    @staticmethod
    def _initialization(
        max_retries: int,
        status_retry_list: List[int],
        status_error_list: List[int],
        until_request_succeed: Union[bool, List[int]]
    ):
        """初始化请求参数"""
        # max_retries
        if (
            not isinstance(max_retries, int)
            or max_retries <= 0
        ):
            raise ValueError(f"'max_retries' initial value must be > 0, got: {max_retries}")

        # status_retry_list
        if not isinstance(status_retry_list, (list, tuple)):
            raise TypeError(f"'status_retry_list' type must be a List[int], got: {type(status_retry_list)}")

        # status_error_list
        if not isinstance(status_error_list, (list, tuple)):
            raise TypeError(f"'status_error_list' type must be a List[int], got: {type(status_error_list)}")

        # until_request_succeed
        if not isinstance(until_request_succeed, (list, tuple)):
            until_request_succeed = [200] if until_request_succeed else []

        return until_request_succeed

    def build_url(self, url: Url) -> Url:
        """基于 base_url 构建绝对路径"""
        _url = self._parse_url(url)
        if not self._is_absolute_url(_url):
            if not self.base_url:
                raise exceptions.InvalidURL(
                    f"scheme: {_url.scheme!r}; netloc: {_url.netloc!r}; path: {_url.path!r}; "
                    f"query: {_url.query!r}; fragment: {_url.fragment!r}. got: {url!r}"
                )
            return parse.urljoin(self.base_url, url)
        return url

    @staticmethod
    def _parse_url(url: Url, /):
        """使用 urllib.parse.urlsplit 解析"""
        if isinstance(url, parse.SplitResult):
            return url

        if not isinstance(url, str):
            raise TypeError(f"'url' type must be a str, got: {type(url)}")

        url = parse.urlsplit(url.strip())
        return url

    def _is_absolute_url(self, url) -> bool:
        """是否为绝对路径"""
        url = self._parse_url(url)
        return bool(url.scheme and url.scheme)

    def _parse_base_url(self, url: Url, /) -> Optional[Url]:
        """获取 base url 值"""
        if (
            url is None
            or not self._is_absolute_url(url)
        ):
            return None
        return url

    @property
    def base_url(self) -> Optional[Url]:
        """base_url"""
        return self._base_url

    @base_url.setter
    def base_url(self, value) -> None:
        self._base_url = self._parse_base_url(value)

    @property
    def user_agent(self) -> str:
        """User_Agent"""
        return self.headers.get("User-Agent")

    @user_agent.setter
    def user_agent(self, value):
        if not isinstance(value, str):
            raise TypeError(f"'value' type must be a str, got: {type(value)}")
        self.headers.update({"User-Agent": value})

    @property
    def console(self):
        """rich.console"""
        return self._console
