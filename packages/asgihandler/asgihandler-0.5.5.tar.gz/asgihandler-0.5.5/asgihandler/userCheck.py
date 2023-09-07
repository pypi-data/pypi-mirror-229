import asyncio
from .handler import fetch_data


class userCheck:
    def get_auth_check(server, host, referer, operator, token, method, path, raw_path):
        context = {
            "server": server,
            "host": host,
            "referer": referer,
            "operator": operator,
            "token": token,
            "version": "2.1.48",
            "method": method,
            "path": path
        }
        asyncio.run(fetch_data(context))