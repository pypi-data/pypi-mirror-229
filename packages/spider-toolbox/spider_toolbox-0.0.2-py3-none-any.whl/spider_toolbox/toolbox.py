import time
import os
import requests
from rich import print


# 请求超时重试
def get(url: str, headers=None, params=None, retry: int = 10, retry_sleep: int = 1):
    """
    :param url: 地址
    :param headers: 请求头
    :param params: params
    :param retry: 重试次数
    :param retry_sleep: 重试休眠时间
    """
    if headers is None:
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
    for i in range(1, retry + 1):
        try:
            resp = requests.get(url, headers=headers, params=params)
            if resp.status_code != 200:
                raise ''
            return resp
        except Exception:
            print(f'{url} [red]失败 {i} 次[/]')
            time.sleep(retry_sleep + i / 3)
    return False


def byte_downloader(url: str,
                    workdir: str,
                    file_name: str,
                    file_type: str,
                    headers=None):
    file_type = file_type.replace('.', '')
    workdir = os.path.join(workdir, file_name) + '.' + file_type
    resp = get(url, headers=headers)
    if resp:
        with open(workdir, 'wb') as f:
            f.write(resp.content)
    else:
        return False
