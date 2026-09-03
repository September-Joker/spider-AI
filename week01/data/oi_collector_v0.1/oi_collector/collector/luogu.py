"""洛谷采集器（进阶练习，未注册到 main.py）。

现状：洛谷有 WAF 防护，requests 直接请求 _contentOnly 接口通常拿不到 JSON，
     需要 Playwright 带浏览器指纹、Cookie 才能正常访问。
     因此当前默认命令行里没有它——这正是你学 Playwright 的第一个目标。

和 Codeforces 的区别（学习重点）：
- 非官方内部接口，结构可能随时变化；
- 需要 Referer / Accept 等请求头，且有反爬拦截；
- 解析时必须"防御性"地取字段，接口一变不能让整个程序崩掉。

启用方式：掌握 Playwright 后，把下面的 _polite_get 换成浏览器渲染版本，
         再到 main.py 的 FETCHERS 里注册 "luogu": LuoguFetcher。

合规提醒：仅用于个人教学、严格限速、不要高频抓取。
"""
from typing import Optional, List, Dict

from .base import BaseFetcher, FetchError


class LuoguFetcher(BaseFetcher):
    name = "luogu"
    LIST_URL = "https://www.luogu.com.cn/problem/list?_contentOnly=1"

    def fetch(self, limit: Optional[int] = None) -> List[Dict]:
        resp = self._polite_get(
            self.LIST_URL,
            headers={
                "Referer": "https://www.luogu.com.cn/problem/list",
                "Accept": "application/json, text/plain, */*",
            },
        )
        try:
            data = resp.json()
        except ValueError as e:
            raise FetchError("洛谷返回的不是 JSON（接口可能已调整，或需要浏览器访问）") from e

        # 防御性解析：路径上任何一层缺失都给出明确报错，而不是 KeyError 堆栈
        try:
            raw = data["currentData"]["problems"]["result"]
        except (KeyError, TypeError) as e:
            raise FetchError(
                "洛谷接口结构已变化。学习练习：打开浏览器 F12 开发者工具，"
                "在 Network 里找到真实请求，对照修正这里的解析路径。"
            ) from e

        if limit:
            raw = raw[:limit]
        return [self._normalize(p) for p in raw]

    @staticmethod
    def _normalize(p: Dict) -> Dict:
        pid = p.get("pid", "")
        return {
            "source": "luogu",
            "source_id": pid,
            "title": (p.get("title") or "").strip(),
            "difficulty": p.get("difficulty"),       # 洛谷难度为数字编号
            "tags": [],   # 洛谷标签是 id->名称 的映射表，留作扩展练习（见 README）
            "url": f"https://www.luogu.com.cn/problem/{pid}",
        }
