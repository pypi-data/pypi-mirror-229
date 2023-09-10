from typing import List, Union, Optional

from pyxk.request._typedef import *
from pyxk.request._sessions import Session


def request(
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
    user_agent: Optional[str] = None
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
    :param user_agent: User Agent
    :return: requests.Response
    """
    with Session(user_agent=user_agent) as session:
        return session.request(
            method=method,
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


def get(
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
    user_agent: Optional[str] = None
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
    :param user_agent: User Agent
    :return: requests.Response
    """
    with Session(user_agent=user_agent) as session:
        return session.request(
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
    user_agent: Optional[str] = None
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
    :param user_agent: User Agent
    :return: requests.Response
    """
    with Session(user_agent=user_agent) as session:
        return session.request(
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
    user_agent: Optional[str] = None
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
    :param user_agent: User Agent
    :return: requests.Response
    """
    with Session(user_agent=user_agent) as session:
        return session.request(
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
    user_agent: Optional[str] = None
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
    :param user_agent: User Agent
    :return: requests.Response
    """
    with Session(user_agent=user_agent) as session:
        return session.request(
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


def patch(
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
    user_agent: Optional[str] = None
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
    :param user_agent: User Agent
    :return: requests.Response
    """
    with Session(user_agent=user_agent) as session:
        return session.request(
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


def put(
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
    user_agent: Optional[str] = None
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
    :param user_agent: User Agent
    :return: requests.Response
    """
    with Session(user_agent=user_agent) as session:
        return session.request(
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


def delete(
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
    user_agent: Optional[str] = None
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
    :param user_agent: User Agent
    :return: requests.Response
    """
    with Session(user_agent=user_agent) as session:
        return session.request(
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


def downloader(
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
    user_agent: Optional[str] = None,
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
    :param user_agent: User Agent
    :param output: 文件输出路径
    :param restore: 文件续传

    :return: requests.Response
    """
    with Session(user_agent=user_agent) as session:
        return session.downloader(
            method=method,
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
            verify=verify,
            cert=cert,
            json=json,
            max_retries=max_retries,
            loading_status=loading_status,
            status_retry_list=status_retry_list,
            status_error_list=status_error_list,
            until_request_succeed=until_request_succeed,
            output=output,
            restore=restore
        )
