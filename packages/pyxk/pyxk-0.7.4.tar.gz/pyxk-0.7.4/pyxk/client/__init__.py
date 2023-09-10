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
from pyxk.client.client import Client, Response
