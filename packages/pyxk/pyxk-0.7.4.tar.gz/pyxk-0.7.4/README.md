# Pyxk

### pyxk install
```console
$ python -m pip install pyxk
```

### pyxk.client
```python
from pyxk.client import Client, Response

class Download(Client):
    start_urls = [
        ("http://www.baidu.com", {"title": "百度", "index": index})
        for index in range(2)
    ]

    async def parse(self, resp: Response, **kwargs):
        print(resp.status, kwargs)

if __name__ == "__main__":
    Download.run()

>>> status_code: 200 {'title': '百度', 'index': 1}
>>> status_code: 200 {'title': '百度', 'index': 0}
```

### pyxk.m3u8
```python
from pyxk.m3u8 import load_m3u8

load_m3u8("https://xxx.xxx", output="xxx.mp4")
```

```console
$ m3u8 --help

Usage: m3u8 [OPTIONS] <M3U8_URL>

  M3U8资源下载器

Options:
  -c, --content TEXT            M3U8内容 or 文件路径
  -o, --output TEXT             M3U8存储路径(默认当前工作目录)
  --no-verify                   请求验证
  -h, --headers <TEXT TEXT>...  Http headers
  -ua, --user-agent TEXT        输入user_agent系统类型, 进行自生成[ios,
                                mac,android,windows,linux]
  -r, --reload                  重载m3u8资源[每次请求网络资源 会在本地生成文件，默认
                                使用本地文件]
  --no-del                      保留m3u8资源[下载完成后默认删 除m3u8文件以及ts
                                文件]
  -l, --limit INTEGER           aiohttp.limit
  -s, --semaphore INTEGER       asyncio.Semaphore
  --help                        Show this message and exit.

# use m3u8 url download
$ m3u8 https://xxx.m3u8 -o xxx.mp4

# use m3u8 file download
$ m3u8 -c index.m3u8 -o xxx.mp4
```