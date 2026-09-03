"""采集器基类：统一处理【限速、重试、请求头】三件事。

学习点：
- 生产级爬虫和教学脚本最大的区别：不相信网络永远正常。
- 限速（对目标网站礼貌）+ 指数退避重试（失败后等 2s、4s、8s 再试）。
- 子类只要实现 fetch()，不用重复关心这些细节。
"""
import time
import logging
from typing import Optional, List, Dict

import requests

import config

log = logging.getLogger("oi.collector")


class FetchError(Exception):
    """采集失败的统一异常。"""


class BaseFetcher:
    name = "base"

    def __init__(self):
        # Session 自动复用 TCP 连接和 Cookie，比每次 requests.get 更高效
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": config.USER_AGENT})
        self._last_request_at = 0.0

    def _polite_get(self, url: str, **kwargs) -> requests.Response:
        """带限速和重试的 GET。所有采集器都应该走这个方法。"""
        # 1) 限速：距离上次请求不足 REQUEST_DELAY 就先睡一会
        wait = config.REQUEST_DELAY - (time.time() - self._last_request_at)
        if wait > 0:
            time.sleep(wait)

        # 2) 指数退避重试
        last_exc = None
        for attempt in range(1, config.MAX_RETRIES + 1):
            try:
                resp = self.session.get(url, timeout=config.REQUEST_TIMEOUT, **kwargs)
                self._last_request_at = time.time()
                resp.raise_for_status()  # HTTP 4xx/5xx 会抛异常
                return resp
            except requests.RequestException as e:
                last_exc = e
                log.warning("[%s] 第 %d 次请求失败：%s", self.name, attempt, e)
                time.sleep(2 ** attempt)  # 2s -> 4s -> 8s
        raise FetchError(f"{url} 连续 {config.MAX_RETRIES} 次请求失败：{last_exc}")

    def fetch(self, limit: Optional[int] = None) -> List[Dict]:
        """返回标准化后的题目字典列表。

        每条记录统一包含字段：
        source / source_id / title / difficulty / tags / url
        子类必须实现本方法。
        """
        raise NotImplementedError
