from typing import List, Union, Optional

from pyxk.utils import path, number, convert_units
from pyxk.progress import download_progress
from pyxk.request._base import BaseSession, CIDict, LazyLoader
from pyxk.request._typedef import *

_box = LazyLoader("_box", globals(), "rich.box")
_live = LazyLoader("_live", globals(), "rich.live")
_table = LazyLoader("_table", globals(), "rich.table")
_panel = LazyLoader("_panel", globals(), "rich.panel")


class Session(BaseSession):
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

    def __exit__(self, *args):
        self.close()

    def __enter__(self) -> "Session":
        return self

    def downloader(
        self,
        url: Url,
        method: Method = "GET",
        *,
        params: Params = None,
        data: Data = None,
        headers: Headers = None,
        cookies: Cookies = None,
        files: Files = None,
        auth: Auth = None,
        timeout: Optional[Union[int, float]] = 10,
        allow_redirects: bool = True,
        proxies: Proxies = None,
        hooks: Hooks = None,
        verify: Optional[Union[bool, str]] = None,
        cert: Cert = None,
        json: Json = None,
        max_retries: int = 10,
        loading_status: bool = True,
        status_retry_list: List[int] = [],
        status_error_list: List[int] = [],
        until_request_succeed: Union[bool, List[int]] = False,
        output: Optional[str] = None,
        restore: bool = False,
    ) -> Response:
        """request.downloader(url, "GET", output=None, restore=True, **kwargs)

        :param url: url
        :param method: default: 'GET' - 'POST', 'HEAD', 'OPTIONS', 'DELETE', 'PUT', 'PATCH'
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
        :param verify: verify ssl
        :param cert: 请求证书
        :param json: jsonm
        :param max_retries: 最大重试次数
        :param loading_status: 请求显示 rich.status
        :param status_retry_list: 状态码重试列表
        :param status_error_list: 状态码错误列表
        :param until_request_succeed: 直到请求成功
        :param output: 文件输出路径
        :param restore: 文件续传

        :return: requests.Response
        """
        # invalid output
        if not isinstance(output, str):
            if output is not None:
                raise TypeError(f"'output' type must be a str, got: {type(output)}")
            file = None
        else:
            output = "_".join(output.strip().split())
            file = path(output, exits_name=True)
            if file.is_dir():
                raise IsADirectoryError(f"Is directory, got: {output!r}")

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
            "stream": True,
            "verify": verify,
            "cert": cert,
            "json": json,
            "max_retries": max_retries,
            "loading_status": loading_status,
            "status_retry_list": status_retry_list,
            "status_error_list": status_error_list,
            "until_request_succeed": until_request_succeed,
        }

        # Head
        head = self.head(url, **request)

        # Content-Type
        content_type = head.headers.get("Content-Type", "")

        # Content-Length
        content_length = number(head.headers.get("Content-Length"), default=0).number
        content_length_string = convert_units(content_length).string

        # rich.table
        table = _table.Table(show_header=False, box=_box.SIMPLE_HEAD)
        table.add_column(justify="left", overflow="fold")
        table.add_row(f"<[cyan]Response[/] [{head.status_code}]> [blue u]{url}[/]")
        table.add_section()
        table.add_row(f"[green]filetype[/]: [yellow]{content_type}[/]")
        table.add_row(f"[green]filesize[/]: [yellow]{content_length_string}[/] ({content_length})")

        # panel
        panel = _panel.Panel(
            table,
            box=_box.ASCII,
            title="[red b]Downloader[/]",
            title_align="center",
            border_style="bright_blue",
            expand=False,
        )

        # 文件可用
        if file:
            table.add_row(f"[green]filename[/]: [blue]{file.name}[/]")
            panel.subtitle = f"[dim i]{file.parent.as_posix()}[/]"
            panel.subtitle_align = "right"
        else:
            self.console.print(panel)
            return head

        # 下载变量
        completed, chunk_size = 0, 1024

        # 文件续传
        if (
            restore
            and file.is_file()
            and content_length
        ):
            file_size = file.stat().st_size
            if file_size <= content_length:
                completed += file_size
                headers = CIDict(headers)
                headers.update({"Range": f"bytes={completed}-{content_length-1}"})
                request["headers"] = headers
            else:
                restore = False
        else:
            restore = False

        # 开启下载
        response = self.request(method=method, url=url, **request)

        # 状态码 416 请求超出 range 范围
        if response.status_code == 416:
            self.console.print(panel)
            return head

        # progress
        progress = download_progress(console=self.console)
        download_task = progress.add_task("", total=content_length, completed=completed)
        table.add_section()
        table.add_row(progress)

        # 创建父级文件夹
        file.parent.mkdir(parents=True, exist_ok=True)

        # 流式下载
        with _live.Live(panel, console=self.console):
            with open(file, "ab" if restore else "wb") as write_file_obj:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    write_file_obj.write(chunk)
                    progress.update(download_task, advance=chunk_size)
        return head

    def get(
        self,
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
        """request("GET", url, **kwargs)

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
        return self.request(
            method="GET",
            url=url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            proxies=proxies,
            hooks=hooks,
            stream=stream,
            verify=verify,
            cert=cert,
            json=json,
            max_retries=max_retries,
            loading_status=loading_status,
            status_retry_list=status_retry_list,
            status_error_list=status_error_list,
            until_request_succeed=until_request_succeed,
        )

    def post(
        self,
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
        """request("POST", url, **kwargs)

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
        return self.request(
            method="POST",
            url=url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            proxies=proxies,
            hooks=hooks,
            stream=stream,
            verify=verify,
            cert=cert,
            json=json,
            max_retries=max_retries,
            loading_status=loading_status,
            status_retry_list=status_retry_list,
            status_error_list=status_error_list,
            until_request_succeed=until_request_succeed,
        )

    def head(
        self,
        url: Url,
        *,
        params: Params = None,
        data: Data = None,
        headers: Headers = None,
        cookies: Cookies = None,
        files: Files = None,
        auth: Auth = None,
        timeout: Optional[Union[int, float]] = 5,
        allow_redirects: bool = False,
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
        """request("HEAD", url, **kwargs)

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
        return self.request(
            method="HEAD",
            url=url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            proxies=proxies,
            hooks=hooks,
            stream=stream,
            verify=verify,
            cert=cert,
            json=json,
            max_retries=max_retries,
            loading_status=loading_status,
            status_retry_list=status_retry_list,
            status_error_list=status_error_list,
            until_request_succeed=until_request_succeed,
        )

    def options(
        self,
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
        """request("OPTIONS", url, **kwargs)

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
        return self.request(
            method="OPTIONS",
            url=url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            proxies=proxies,
            hooks=hooks,
            stream=stream,
            verify=verify,
            cert=cert,
            json=json,
            max_retries=max_retries,
            loading_status=loading_status,
            status_retry_list=status_retry_list,
            status_error_list=status_error_list,
            until_request_succeed=until_request_succeed,
        )

    def delete(
        self,
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
        """request("DELETE", url, **kwargs)

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
        return self.request(
            method="DELETE",
            url=url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            proxies=proxies,
            hooks=hooks,
            stream=stream,
            verify=verify,
            cert=cert,
            json=json,
            max_retries=max_retries,
            loading_status=loading_status,
            status_retry_list=status_retry_list,
            status_error_list=status_error_list,
            until_request_succeed=until_request_succeed,
        )

    def put(
        self,
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
        """request("PUT", url, **kwargs)

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
        return self.request(
            method="PUT",
            url=url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            proxies=proxies,
            hooks=hooks,
            stream=stream,
            verify=verify,
            cert=cert,
            json=json,
            max_retries=max_retries,
            loading_status=loading_status,
            status_retry_list=status_retry_list,
            status_error_list=status_error_list,
            until_request_succeed=until_request_succeed,
        )

    def patch(
        self,
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
        """request("PATCH", url, **kwargs)

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
        return self.request(
            method="PATCH",
            url=url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            proxies=proxies,
            hooks=hooks,
            stream=stream,
            verify=verify,
            cert=cert,
            json=json,
            max_retries=max_retries,
            loading_status=loading_status,
            status_retry_list=status_retry_list,
            status_error_list=status_error_list,
            until_request_succeed=until_request_succeed,
        )
