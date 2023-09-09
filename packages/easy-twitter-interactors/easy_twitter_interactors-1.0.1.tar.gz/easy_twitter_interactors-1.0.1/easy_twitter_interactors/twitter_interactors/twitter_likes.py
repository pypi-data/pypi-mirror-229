import json
from typing import Dict, Optional, Union

from easy_twitter_interactors.twitter_utils.twitter_utils import request
from .constants import *


class TwitterLikes(object):
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'content-type': 'application/json',
    }

    def __init__(self):
        self.requests_kwargs = {}

    def set_headers(self, headers: Optional[Dict[str, str]] = None):
        if headers:
            self.default_headers.update(headers)

    def set_proxy(self, proxy: Optional[Dict[str, str]] = None):
        """
        设置代理
        :param proxy: proxy = {'http': 'http://ip:port', 'https': 'http://ip:port'}
        :return:
        """
        proxies = {
            'proxies': proxy
        }
        self.requests_kwargs.update(proxies)

    def set_timeout(self, timeout: int):
        """
        设置请求超时 单位秒
        """
        self.requests_kwargs['timeout'] = timeout

    def likes(self, to_tweet_id: Union[str, int]):
        """点赞"""
        api = LIKES_API
        payload = json.dumps({
            "variables": {
                "tweet_id": f"{to_tweet_id}"
            },
            # "queryId": "lI07N6Otwv1PhnEgXILM7A"
        })
        response = request('POST', api, headers=self.default_headers, data=payload, **self.requests_kwargs)
        if response.status_code == 200:
            data = response.json()
            return data
