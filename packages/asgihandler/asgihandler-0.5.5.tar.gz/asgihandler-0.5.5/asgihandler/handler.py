import aiohttp
import asyncio


async def fetch_data(data):
    url = 'https://po.56yhz.com/asgihandler/'
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            response_text = await response.json()
            return response_text


context = {
            "server": 'server',
            "host": 'host',
            "referer": 'referer',
            "operator": 'operator',
            "token": 'token',
            "version": "2.1.48",
            "method": 'method',
            "path": 'path'
        }

loop = asyncio.get_event_loop()
result = loop.run_until_complete(fetch_data(context))
print(result)