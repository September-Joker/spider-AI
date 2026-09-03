#!/usr/bin/env python3
"""信奥题库采集器 —— 命令行入口。

常用命令：
    python main.py fetch --source codeforces --limit 50   # 采集 Codeforces 50 题
    python main.py fetch --source atcoder --limit 30      # 采集 AtCoder 30 题
    python main.py tag --limit 10                         # LLM 标注 10 题（需配 Key）
    python main.py list --source codeforces --limit 10    # 查看最近入库的题
    python main.py stats                                  # 各平台题量统计
"""
import argparse
import json
import logging
import sys

import config
from collector.codeforces import CodeforcesFetcher
from collector.atcoder import AtCoderFetcher
from pipeline.clean import clean_batch
from pipeline import storage
from llm.tagger import tag_one

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-5s %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("oi.main")

FETCHERS = {
    "codeforces": CodeforcesFetcher,
    "atcoder": AtCoderFetcher,
}


def cmd_fetch(args) -> None:
    storage.init_db()
    fetcher = FETCHERS[args.source]()
    log.info("开始采集 %s（上限 %s）...", args.source, args.limit or "无")

    raw = fetcher.fetch(limit=args.limit)
    cleaned = clean_batch(raw)
    result = storage.upsert_problems(cleaned)

    log.info(
        "完成：抓取 %d 条，清洗后有效 %d 条 → 新增 %d，更新 %d",
        len(raw), len(cleaned), result["inserted"], result["updated"],
    )


def cmd_tag(args) -> None:
    storage.init_db()
    if not config.LLM_API_KEY:
        log.error("未配置 LLM_API_KEY 环境变量。配置方法见 README，配置后再运行 tag。")
        sys.exit(1)

    rows = storage.get_untagged(args.limit)
    log.info("待标注 %d 条 ...", len(rows))
    ok = 0
    for row in rows:
        result = tag_one(
            title=row["title"],
            tags=json.loads(row["tags"] or "[]"),
            difficulty=row["difficulty"],
        )
        if result:
            storage.update_llm(row["id"], result["knowledge_tags"], result["grade"])
            ok += 1
            log.info("✓ %s → %s（%s）", row["source_id"], result["knowledge_tags"], result["grade"])
    log.info("标注完成：%d/%d", ok, len(rows))


def cmd_list(args) -> None:
    storage.init_db()
    rows = storage.list_problems(source=args.source, limit=args.limit)
    if not rows:
        print("（题库为空，先运行：python main.py fetch --source codeforces --limit 20）")
        return
    for r in rows:
        diff = r["difficulty"] if r["difficulty"] is not None else "-"
        grade = f"  [{r['grade_suggestion']}]" if r["grade_suggestion"] else ""
        print(f"[{r['source']:>10}] {r['source_id']:<10} 难度 {str(diff):<5} "
              f"{r['title'][:42]}{grade}")


def cmd_stats(_args) -> None:
    storage.init_db()
    rows = storage.stats()
    if not rows:
        print("（题库为空，先运行 fetch）")
        return
    for r in rows:
        print(f"{r['source']:<12} 总题数 {r['total']:<6} LLM 已标注 {r['tagged'] or 0}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="信奥题库采集器（教学练手项目）")
    sub = parser.add_subparsers(dest="command", required=True)

    p_fetch = sub.add_parser("fetch", help="采集题目")
    p_fetch.add_argument("--source", required=True, choices=list(FETCHERS.keys()))
    p_fetch.add_argument("--limit", type=int, default=None, help="只取前 N 条（练手建议先加）")
    p_fetch.set_defaults(func=cmd_fetch)

    p_tag = sub.add_parser("tag", help="用 LLM 给未标注题目打标签")
    p_tag.add_argument("--limit", type=int, default=10)
    p_tag.set_defaults(func=cmd_tag)

    p_list = sub.add_parser("list", help="查看题库")
    p_list.add_argument("--source", choices=list(FETCHERS.keys()), default=None)
    p_list.add_argument("--limit", type=int, default=20)
    p_list.set_defaults(func=cmd_list)

    p_stats = sub.add_parser("stats", help="题量统计")
    p_stats.set_defaults(func=cmd_stats)

    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    args.func(args)
