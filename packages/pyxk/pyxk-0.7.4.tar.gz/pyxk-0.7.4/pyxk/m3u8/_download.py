import time
import shlex
import subprocess
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

import aiofiles
from rich.console import Console

from pyxk.client import Client, Response
from pyxk.progress import download_progress
from pyxk.utils import md5, path, rename, user_agents
from pyxk.m3u8._typedef import Path, Store, Output, Content, RichResult


class M3u8Downloader(Client):

    limit = 300
    timeout = 10
    warning = False
    allowable = dict(
        url=(str, type(None)),
        content=(str, bytes, type(None)),
        store=(str, Path, type(None)),
        output=(str, Path, type(None)),
        delete=(bool,),
        reload=(bool,)
    )
    semaphore = 16
    user_agent = user_agents.android
    max_retries = 15
    status_error_list = list(range(400, 411))
    until_request_succeed = True

    def __init__(
        self,
        content: Optional[Content] = None,
        url: Optional[str] = None,
        store: Optional[Store] = None,
        output: Optional[Output] = None,
        delete: bool = True,
        reload: bool = False,
        **kwargs
    ):
        super().__init__(**kwargs)
        # 所有数据
        self._attrs = dict(
            url=url,
            content=content,
            store=store,
            output=output,
            delete=delete,
            reload=reload
        )
        self.allowed(**self._attrs)
        self._initialization()

        self.rich: Optional[RichResult] = None
        self.files: list = []
        self.cipher: dict = {}
        self.console: Console = Console()

    def _initialization(self):
        """初始化"""
        self.store = self._attrs["store"]
        self.output = self._attrs["output"]
        # 创建文件夹
        if self.output is not None:
            self.temp_folder.mkdir(parents=True, exist_ok=True)

    async def parse(self, resp: Response, file: Path, key: Optional[str]):
        """解析每个ts文件内容"""
        content = await resp.content.read()
        # 解密content
        if key:
            content = self.cipher[key].decrypt(content)
        # 保存content
        async with aiofiles.open(file, "wb") as write_file_obj:
            # 本地存储
            await write_file_obj.write(content)
        # 更新进度条
        self.rich.progress.update(self.rich.task, advance=1)

    async def completed(self, *args, **kwargs):
        """使用模块ffmpeg合并m3u8"""
        if not self.files:
            return

        # 创建 filelist 文件
        filelist, filesize = self.temp_folder.joinpath("filelist.txt"), 0
        with open(filelist, "w", encoding="utf-8") as write_fileobj:
            for file in self.files:
                write_fileobj.write(f"file '{file.as_posix()}'\n")
                filesize += file.stat().st_size

        # ffmpeg 视频合并代码, 监测合并完成状态
        args = shlex.split(f"ffmpeg -loglevel quiet -f concat -safe 0 -i {filelist} -c copy {self.output} -y")
        merge_completed = False

        # ffmpeg 合并函数
        def merge_segments():
            try:
                subprocess.run(args=args, check=True)
            except FileNotFoundError:
                self.console.log("[red]ffmpeg is not available![/]")
            finally:
                nonlocal merge_completed
                merge_completed = True

        # 显示合并进度条
        def merge_progress():
            # 没有ffmpeg 直接退出
            time.sleep(0.25)
            if merge_completed:
                return
            # 当前文件大小
            current_filesize = lambda: self.output.stat().st_size if self.output.is_file() else 0
            # 合并进度条
            progress = download_progress(transient=True)
            task = progress.add_task(description="", total=filesize, visible=False)
            self.rich.table.add_row(progress)

            while True:
                # 停止循环
                if merge_completed:
                    progress.update(task, completed=filesize, visible=False)
                    break
                progress.update(task, completed=current_filesize(), visible=True)
                time.sleep(0.25)

        # 开启多线程(ts文件合并和进度条显示)
        pool = ThreadPoolExecutor()
        pool.submit(merge_segments)
        pool.submit(merge_progress)
        pool.shutdown()

    @staticmethod
    def is_m3u8(content: Content) -> bool:
        """判断content是否属于m3u8文档"""
        if isinstance(content, str):
            return content.startswith("#EXTM3U")
        if isinstance(content, bytes):
            return content.startswith(b"#EXTM3U")
        return False

    def generate_filename(self, url: str, is_key_file: bool = False):
        """根据url生成完整文件路径(使用MD5加工url)"""
        self.allowed(url=url)
        if url is None or self.output is None:
            return None
        suffix = ".key" if is_key_file else ".m3u8"
        base_name = md5(url).ciphertext + suffix
        return self.temp_folder.joinpath(base_name)

    @property
    def output(self) -> Optional[Path]:
        """文件存储完整路径"""
        return self._attrs["output"]

    @output.setter
    def output(self, value) -> Path:
        self.allowed(output=value)
        if value is None:
            self._attrs["output"] = None
            return
        # 去除空格
        value = "_".join(value.strip().split())
        output = self.store.joinpath(value).resolve()
        # output 不能是文件夹
        if output.is_dir():
            raise IsADirectoryError(f"output: {output.as_posix()!r} is a directory. Expect: Is a file")
        # output 去重
        output = rename(output, suffix=".mp4").rename
        # 根据 output更新 store
        if output.parent != self.store:
            self._attrs["store"] = output.parent
        self._attrs["output"] = output

    @property
    def store(self) -> Path:
        """output文件夹路径"""
        return self._attrs["store"]

    @store.setter
    def store(self, value):
        self.allowed(store=value)
        if value is None:
            self._attrs["store"] = path()
            return
        store = path(value)
        # 不能是一个文件
        if store.is_file():
            raise FileExistsError(f"store: {store.as_posix()!r} is a file. Expect: Is a directory")
        self._attrs["store"] = store
        # 更改 output文件夹
        if isinstance(self.output, Path):
            self.output = self.output.name

    @property
    def temp_folder(self) -> Optional[Path]:
        """m3u8文件(ts文件) 和 m3u8密钥 保存文件夹"""
        if self.output is None:
            return None
        base_name = self.output.stem + "_temp"
        return self.store.joinpath(base_name)
