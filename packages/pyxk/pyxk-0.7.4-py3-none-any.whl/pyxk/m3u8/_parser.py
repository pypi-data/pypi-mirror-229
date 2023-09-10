from typing import Optional

from m3u8 import loads
from pyxk.m3u8._typedef import Content, ParseResult


class M3u8Parser:

    def __init__(self, content: Content, url: Optional[str], m3u8: object):
        self.url = url
        self.m3u8 = m3u8
        self.parse = loads(content, url)

    async def start_parse(self) -> ParseResult:
        """开始解析m3u8文件"""
        self.parse, self.url = await self.parse_playlists(self.parse, self.url)
        keys = await self.parse_m3u8keys()
        segments, durations = self.parse_segments()
        return ParseResult(self.url, keys, segments, durations)

    async def parse_playlists(self, parse, url=None):
        """解析 m3u8 playlists"""
        # 没有 playlists
        if not parse.is_variant:
            return parse, url

        def sorted_playlists(playlist):
            """对 playlists 进行排序"""
            playlist.uri = playlist.absolute_uri
            return playlist.stream_info.bandwidth

        # 对 playlists 进行排序
        playlists = sorted(parse.playlists, key=sorted_playlists)

        # 保存m3u8文件
        self.m3u8.sava_m3u8_content(url, parse.dumps())

        # 获取带宽最大的 playlist
        new_url = playlists[-1].uri
        new_parse = loads(
            await self.m3u8.get_m3u8_content(new_url),
            new_url
        )
        return await self.parse_playlists(new_parse, new_url)

    async def parse_m3u8keys(self) -> dict:
        """解析 m3u8 keys"""
        keys = {}
        for key in self.parse.keys:
            # 无效key
            if not key:
                continue
            key.uri = key.absolute_uri
            # 获取 密钥 和 偏移量
            secret = (await self.m3u8.get_m3u8_content(key.uri, True))[:16]
            iv = key.iv.removeprefix("0x")[:16].encode() if key.iv else secret
            # 保存key
            keys[key.uri] = {"key": secret, "iv": iv}
            # 保存密钥到本地
            self.m3u8.sava_m3u8_content(key.uri, secret, True)
        return keys

    def parse_segments(self) -> tuple:
        """解析 m3u8 segments"""
        # 无效的 m3u8 文件
        if not self.parse.is_endlist:
            return None, None
        # all segments
        segments, durations = [], 0

        for index, segment in enumerate(self.parse.segments):
            # segments 绝对路径
            segment.uri = segment.absolute_uri
            # segment key
            key = segment.key.uri if segment.key else None
            # 保存 segment
            file = self.m3u8.temp_folder.joinpath(f"{index}.ts") if self.m3u8.output else None
            item = (segment.uri, {"file": file, "key": key})
            segments.append(item)
            # segment 时间累加
            durations += segment.duration
        # 保存 m3u8 文件
        self.m3u8.sava_m3u8_content(self.url, self.parse.dumps())
        return segments, durations

    @classmethod
    async def run(cls, content: Content, url: Optional[str], m3u8: object) -> ParseResult:
        """开始解析m3u8文件"""
        self = cls(content, url, m3u8)
        return await self.start_parse()
