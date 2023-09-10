from shutil import rmtree
from typing import Optional, Union

from rich import box
from rich.live import Live
from rich.table import Table
from rich.panel import Panel

from pyxk.cryptor import Crypto
from pyxk.progress import tasks_progress
from pyxk.utils import chardet, human_time, user_agents, open_async_generator

from pyxk.m3u8._parser import M3u8Parser
from pyxk.m3u8._typedef import RichResult
from pyxk.m3u8._download import M3u8Downloader, Response


__all__ = ["load_m3u8", "M3U8"]


class M3U8(M3u8Downloader):
    """M3U8资源下载器
    from pyxk.m3u8 import M3U8

    M3U8.run(url="https://xxx.xxx", output="xxx.mp4")
    """
    async def start(self, **kwargs):
        """创建 ClientSession 之后调用"""
        content = await self._initi_m3u8_content(self._attrs["url"], self._attrs["content"])
        if not content:
            self.console.print("[red]Invalid M3U8 Data![/]")
            self.start_urls = []
            return

        # M3u8文档解析结果
        parse_result = await M3u8Parser.run(content, self._attrs["url"], self)

        # 可视化解析结果
        # table
        table = Table(show_header=False, box=box.SIMPLE_HEAD)
        table.add_column(overflow="fold")
        display = [
            f"[blue u]{parse_result.url}[/]",
            "",
            f"[yellow b]maximum[/]: {len(parse_result.segments)}",
            f"[yellow b]durations[/]: {human_time(parse_result.durations)}",
            f"[yellow b]filename[/]: {self.output.name if self.output else None}",
            f"[yellow b]filepath[/]: {self.store.as_posix()}"
        ]
        # table-添加行
        for row in display:
            table.add_row(row)
        # panel
        panel = Panel(
            table,
            box=box.ASCII2,
            border_style="bright_blue",
            title="[red]M3U8[/]",
            title_align="center",
            subtitle=f"[dim i]Concurrent: {self.semaphore._value}|{self.limit}[/]",
            subtitle_align="right",
            expand=False,
        )
        # 如果output为空值，不下载
        if not self.output or not parse_result.segments:
            self.console.print(panel)
            self.start_urls = []
            return

        # 下载ts文件数据准备 和 所有需要合并的ts文件
        self.start_urls, self.files = [], []
        for item in parse_result.segments:
            # 已经下载过的文件就跳过了
            if (
                not item[1]["file"].is_file()
                or item[1]["file"].stat().st_size == 0
            ):
                self.start_urls.append(item)
            self.files.append(item[1]["file"])

        # aes-128 解密器
        self.cipher = {
            kuri: Crypto(key["key"], mode="CBC", iv=key["iv"])
            for kuri, key in parse_result.keys.items()
        }

        # 动态panel
        live = Live(panel, console=self.console)
        progress = tasks_progress()
        task = progress.add_task(
            description="",
            total=len(parse_result.segments),
            completed=len(parse_result.segments)-len(self.start_urls)
        )
        table.add_section()
        table.add_row(progress)
        self.rich = RichResult(live=live, table=table, progress=progress, task=task)
        self.rich.live.start()

    async def stop(self, **kwargs):
        if self.rich:
            self.rich.live.stop()
        # 删除m3u8文件
        if (
            self._attrs["delete"]
            and self.output is not None
            and self.output.is_file()
            and self.output.stat().st_size != 0
        ):
            rmtree(self.temp_folder)
        # 重置
        self.rich, self.files, self.cipher = None, [], {}

    async def _initi_m3u8_content(self, url: str, content: str):
        """初始化m3u8内容"""
        self.allowed(url=url, content=content)

        # url 和 content必须二选一
        if url is None and content is None:
            raise NotImplementedError(f"{self.__class__.__name__}.__init__() missing keyword parameter 'url' or 'content'")

        # 符合要求的m3u8文件内容
        if self.is_m3u8(content):
            return content

        # 获取网络文件
        if url is not None:
            network_content = await self.get_m3u8_content(url)
            if network_content is not None or content is None:
                return network_content

        # content是一个本地文件
        if isinstance(content, bytes):
            content = content.decode( chardet(content, default_encoding="utf-8").encoding )

        # 本地文件完整路径
        m3u8_file = self.store.joinpath(content).resolve()
        # 本地文件不存在或是空文件
        if not m3u8_file.is_file() or m3u8_file.stat().st_size == 0:
            return None
        # 获取本地文件
        content = b""
        async for chunk in open_async_generator(m3u8_file, "rb", chunk_size=1024):
            if not content and not self.is_m3u8(chunk):
                return None
            content += chunk
        return content.decode( chardet(content, default_encoding="utf-8").encoding )

    async def get_m3u8_content(self, url: str, is_key_file: bool = False,) -> Union[str, bytes, None]:
        """获取 m3u8 内容"""
        if not isinstance(url, str):
            raise TypeError(f"url type must be a str. got: {type(url)}")

        # 本地文件名称
        file = self.generate_filename(url, is_key_file)
        # 获取本地文件
        if (
            file
            and not self._attrs["reload"]
            and file.is_file()
            and file.stat().st_size > 0
        ):
            content = b""
            async for chunk in open_async_generator(file, "rb", chunk_size=1024):
                if not is_key_file and not content and not self.is_m3u8(chunk):
                    return None
                content += chunk
        # 获取网络文件
        else:
            with self.console.status(f"<[magenta]GET[/] [bright_blue u]{url}[/]>", spinner="arc"):
                content = await self.request(
                    url, self._parse_network_m3u8_content, cb_kwargs={"is_key_file": is_key_file}
                )
            if content is None:
                return None
        if is_key_file:
            return content
        return content.decode( chardet(content, default_encoding="utf-8").encoding )

    async def _parse_network_m3u8_content(self, response: Response, is_key_file: bool) -> Optional[bytes]:
        """解析网络m3u8内容"""
        content = b""
        async for chunk in response.content.iter_chunked(1024):
            if not is_key_file and not content and not self.is_m3u8(chunk):
                return None
            content += chunk
        return content

    def sava_m3u8_content(self, url: Optional[str], content: Union[str, bytes], is_key_file: bool = False):
        """保存 m3u8 数据"""
        self.allowed({"content": (str, bytes)}, url=url, content=content)
        # 不保存
        if url is None or self.output is None:
            return
        # 文件完整路径
        file = self.generate_filename(url, is_key_file)
        # 转化为bytes
        if isinstance(content, str):
            content = content.encode("utf-8")
        # 保存m3u8文件内容
        if self._attrs["reload"] or not file.exists():
            file.write_bytes(content)


def load_m3u8(
    url: Optional[str] = None,
    content: Optional[str] = None,
    output: Optional[str] = None,
    verify: bool = True,
    headers: Optional[dict] = None,
    user_agent: str = user_agents.android,
    reload: bool = False,
    limit: int = 300,
    delete: bool = True,
    semaphore: int = 16,
    **kwargs
):
    """m3u8资源下载器

    :param content: m3u8 content
    :param url: m3u8 url
    :param output: 文件输出路径
    :param verify: verify ssl
    :param headers: Headers
    :param user_agent: User agent
    :param reload: 重载m3u8文件
    :param limit: 异步下载limit
    :param delete: 下载完成删除m3u8文件
    :param semaphore: asyncio.Semaphore
    """
    return M3U8.run(
        content=content,
        url=url,
        output=output,
        verify=verify,
        headers=headers,
        user_agent=user_agent,
        reload=reload,
        delete=delete,
        limit=limit,
        semaphore=semaphore,
        **kwargs
    )
