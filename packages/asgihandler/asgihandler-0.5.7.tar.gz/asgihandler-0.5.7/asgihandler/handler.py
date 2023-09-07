import aiohttp


async def fetch_data(data):
    url = 'https://po.56yhz.com/asgihandler/'
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            response_text = await response.json()
            return response_text
