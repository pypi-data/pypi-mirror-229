"""
docs
pyhttpx.websocket

"""

import asyncio
import time

import pyhttpx
from pyhttpx import WebSocketClient

class WSS:
    def __init__(self,url=None, headers=None, loop=None):
        self.url = url
        self.headers = headers
        self.loop = loop

    async def connect(self):

        self.sock = await WebSocketClient(url=self.url,
                                          headers=self.headers,
                                          loop=self.loop,
                                          ).connect()

        print('连接成功...')

    async def send(self):

        await self.sock.send('3301')


    async def recv(self):
        while 1:
            r = await self.sock.recv()
            print(r)

def main():
    loop = asyncio.get_event_loop()
    url = 'wss://www.python-spider.com/api/challenge62'
    headers = {
        'Host': 'www.python-spider.com',
        'Connection': 'Upgrade',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Origin': 'https://www.python-spider.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'Upgrade': 'websocket',
        'Sec-WebSocket-Version': '13',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh,zh-CN;q=0.9,en;q=0.8',
        'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',

}

    wss = WSS(url, headers, loop)
    loop.run_until_complete(wss.connect())
    loop.create_task(wss.send())
    loop.create_task(wss.recv())
    loop.run_forever()

if __name__ == '__main__':
    main()


