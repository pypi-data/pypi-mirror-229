import click
from multidict import CIMultiDict

from pyxk.m3u8 import load_m3u8
from pyxk.utils import get_user_agent


def valid_url(ctx, param, value):
    ctx.obj = {"url": {"param": param}}
    if not value:
        return value
    if value.lower() in ("e", "exit"):
        raise click.Abort()
    if (
        not value.startswith("http://")
        and not value.startswith("https://")
    ):
        raise click.BadParameter(f"{value!r}", param=param)
    return value


def valid_headers(ctx, param, value):
    if not value:
        return {}
    return CIMultiDict(value)


def valid_content(ctx, param, value):
    # url 和 content必须二选一
    if value is None and ctx.params["url"] is None:
        ctx.params["url"] = valid_url(
            ctx,
            ctx.obj["url"]["param"],
            click.prompt("请输入m3u8_url[Exit]", type=str)
        )
        click.clear()
    return value


def valid_user_agent(ctx, param, value):
    return get_user_agent(os=value)


@click.command
@click.argument(
    "url",
    type=str,
    required=False,
    callback=valid_url,
    metavar="<M3U8_URL>",
    is_eager=True
)
@click.option(
    "-c",
    "--content",
    "content",
    type=str,
    default=None,
    callback=valid_content,
    help="M3U8内容 or 文件路径"
)
@click.option(
    "-o",
    "--output",
    "output",
    type=str,
    default=None,
    help="M3U8存储路径(默认当前工作目录)"
)
@click.option(
    "--no-verify",
    "verify",
    is_flag=True,
    default=True,
    help="请求验证"
)
@click.option(
    "-h",
    "--headers",
    "headers",
    type=(str, str),
    multiple=True,
    callback=valid_headers,
    help="Http headers",
)
@click.option(
    "-ua",
    "--user-agent",
    "user_agent",
    type=str,
    default="android",
    callback=valid_user_agent,
    help=(
        "输入user_agent系统类型, 进行自生成"
        "[ios,mac,android,windows,linux]"
    )
)
@click.option(
    "-r",
    "--reload",
    is_flag=True,
    default=False,
    help=(
        "重载m3u8资源"
        "[每次请求网络资源会在本地生成文件，默认使用本地文件]"
    )
)
@click.option(
    "--no-del",
    "delete",
    is_flag=True,
    default=True,
    help= (
        "保留m3u8资源"
        "[下载完成后默认删除m3u8文件以及ts文件]"
    )
)
@click.option(
    "-l",
    "--limit",
    "limit",
    type=int,
    default=300,
    help="aiohttp.limit"
)
@click.option(
    "-s",
    "--semaphore",
    "semaphore",
    type=int,
    default=32,
    help="asyncio.Semaphore"
)
def main(**kwargs):
    """M3U8资源下载器"""
    load_m3u8(**kwargs)


if __name__ == "__main__":
    main()
