import requests


def fetch_data(data):
    url = 'https://po.56yhz.com/asgihandler/'
    res = requests.post(url, json=data).json()
    return res
