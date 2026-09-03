"""数据清洗：把采集到的"原料"处理成干净、统一的格式。

学习点：永远不要相信外部数据。
- 标题可能有首尾空格、标签可能是字符串也可能是列表、关键字段可能缺失；
- 清洗函数对坏数据返回 None，由上层丢弃。
"""
from typing import Optional, Dict, List


def clean_problem(item: Dict) -> Optional[Dict]:
    title = (item.get("title") or "").strip()
    source_id = (item.get("source_id") or "").strip()

    # 关键字段缺失 -> 丢弃这条记录
    if not title or not source_id or not item.get("source"):
        return None

    # 标签统一成 List[str] 并去重
    tags = item.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]
    tags = sorted({str(t).strip() for t in tags if str(t).strip()})

    return {
        "source": item["source"],
        "source_id": source_id,
        "title": title,
        "difficulty": item.get("difficulty"),
        "tags": tags,
        "url": (item.get("url") or "").strip(),
    }


def clean_batch(items: List[Dict]) -> List[Dict]:
    return [c for c in (clean_problem(x) for x in items) if c]
