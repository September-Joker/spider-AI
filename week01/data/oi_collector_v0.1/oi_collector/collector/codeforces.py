"""Codeforces 采集器 —— 使用官方公开 API，最适合第一个练手对象。

为什么从它开始：
- 官方 API，合法稳定，不需要登录、不需要反爬对抗；
- 题目量大、质量高，是信奥选手常备训练场；
- 返回标准 JSON，解析简单，能快速跑通"采集->存储"全链路。

API 文档：https://codeforces.com/apiHelp/methods
"""
from typing import Optional, List, Dict

from .base import BaseFetcher


class CodeforcesFetcher(BaseFetcher):
    name = "codeforces"
    API_URL = "https://codeforces.com/api/problemset.problems"

    def fetch(self, limit: Optional[int] = None) -> List[Dict]:
        resp = self._polite_get(self.API_URL)
        data = resp.json()

        if data.get("status") != "OK":
            raise RuntimeError(f"Codeforces API 返回异常：{data.get('comment')}")

        problems = data["result"]["problems"]
        if limit:
            problems = problems[:limit]
        return [self._normalize(p) for p in problems]

    @staticmethod
    def _normalize(p: Dict) -> Dict:
        """把 CF 的原始字段转换成我们的统一格式（适配层思想）。"""
        contest_id = p.get("contestId")
        index = p.get("index", "")
        source_id = f"{contest_id}{index}" if contest_id else index
        return {
            "source": "codeforces",
            "source_id": source_id,
            "title": (p.get("name") or "").strip(),
            "difficulty": p.get("rating"),          # CF 评分（整数），没有 rating 的题为 None
            "tags": p.get("tags", []),              # 英文标签列表
            "url": f"https://codeforces.com/problemset/problem/{contest_id}/{index}"
                   if contest_id else "",
        }
