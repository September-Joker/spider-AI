"""AtCoder 采集器 —— AtCoder Problems 社区公开 API。

特点（和 Codeforces 对比着学）：
- 同样是免费公开 API，但这是"社区维护"的第三方数据服务，
  字段风格、数据结构完全不同——体会为什么要写 _normalize 适配层；
- 题目量大（全量上万题），练手时务必加 --limit；
- 难度数据在另一个接口 problem-models.json，留作扩展练习：
  https://kenkoooo.com/atcoder/resources/problem-models.json

接口说明：https://github.com/kenkoooo/AtCoderProblems/blob/master/doc/api.md
"""
from typing import Optional, List, Dict

from .base import BaseFetcher


class AtCoderFetcher(BaseFetcher):
    name = "atcoder"
    PROBLEMS_URL = "https://kenkoooo.com/atcoder/resources/problems.json"

    def fetch(self, limit: Optional[int] = None) -> List[Dict]:
        resp = self._polite_get(self.PROBLEMS_URL)
        data = resp.json()
        if limit:
            data = data[:limit]
        return [self._normalize(p) for p in data]

    @staticmethod
    def _normalize(p: Dict) -> Dict:
        pid = p.get("id", "")
        contest_id = p.get("contest_id", "")
        # title 形如 "A. xxx"，name 是纯题名
        title = (p.get("title") or p.get("name") or "").strip()
        return {
            "source": "atcoder",
            "source_id": pid,
            "title": title,
            "difficulty": None,   # 扩展练习：从 problem-models.json 补 difficulty
            "tags": [],
            "url": f"https://atcoder.jp/contests/{contest_id}/tasks/{pid}"
                   if contest_id else "",
        }
