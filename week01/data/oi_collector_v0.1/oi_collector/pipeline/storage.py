"""SQLite 存储：零配置数据库，upsert 自动去重。

学习点：
- 为什么先用 SQLite 而不是 MySQL：一个文件就是整个库，不用装服务，
  练手阶段最省心；以后换 MySQL 只需要改连接方式，SQL 语句基本不变。
- upsert（存在就更新、不存在就插入）是爬虫去重的核心套路：
  靠 UNIQUE(source, source_id) 约束保证同一道题不会存两份。
"""
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS problems (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    source            TEXT    NOT NULL,
    source_id         TEXT    NOT NULL,
    title             TEXT    NOT NULL,
    difficulty        INTEGER,
    tags              TEXT,              -- JSON 数组：平台自带标签
    url               TEXT,
    llm_tags          TEXT,              -- JSON 数组：LLM 生成的知识点标签
    grade_suggestion  TEXT,              -- LLM 建议的适合年级
    fetched_at        TEXT    NOT NULL,
    tagged_at         TEXT,
    UNIQUE(source, source_id)
);
"""


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row   # 查询结果可以按列名访问
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def upsert_problems(items: List[Dict]) -> Dict[str, int]:
    """插入或更新题目，返回 {"inserted": 新增数, "updated": 更新数}。"""
    now = datetime.now().isoformat(timespec="seconds")
    inserted = updated = 0
    conn = get_conn()
    try:
        for it in items:
            params = {
                "source": it["source"],
                "source_id": it["source_id"],
                "title": it["title"],
                "difficulty": it.get("difficulty"),
                "tags": json.dumps(it.get("tags", []), ensure_ascii=False),
                "url": it.get("url", ""),
                "fetched_at": now,
            }
            try:
                conn.execute(
                    """INSERT INTO problems
                       (source, source_id, title, difficulty, tags, url, fetched_at)
                       VALUES (:source, :source_id, :title, :difficulty, :tags, :url, :fetched_at)""",
                    params,
                )
                inserted += 1
            except sqlite3.IntegrityError:
                # 唯一约束冲突 = 这道题已存在 -> 更新
                conn.execute(
                    """UPDATE problems SET
                         title=:title, difficulty=:difficulty, tags=:tags,
                         url=:url, fetched_at=:fetched_at
                       WHERE source=:source AND source_id=:source_id""",
                    params,
                )
                updated += 1
        conn.commit()
    finally:
        conn.close()
    return {"inserted": inserted, "updated": updated}


def list_problems(source: Optional[str] = None, limit: int = 20) -> List[sqlite3.Row]:
    conn = get_conn()
    try:
        sql = "SELECT * FROM problems"
        params: list = []
        if source:
            sql += " WHERE source = ?"
            params.append(source)
        sql += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def get_untagged(limit: int = 20) -> List[sqlite3.Row]:
    """取还没有 LLM 标注的题目。"""
    conn = get_conn()
    try:
        return conn.execute(
            "SELECT * FROM problems WHERE tagged_at IS NULL ORDER BY id LIMIT ?",
            (limit,),
        ).fetchall()
    finally:
        conn.close()


def update_llm(row_id: int, llm_tags: List[str], grade: str) -> None:
    with get_conn() as conn:
        conn.execute(
            """UPDATE problems SET llm_tags = ?, grade_suggestion = ?, tagged_at = ?
               WHERE id = ?""",
            (json.dumps(llm_tags, ensure_ascii=False), grade,
             datetime.now().isoformat(timespec="seconds"), row_id),
        )


def stats() -> List[sqlite3.Row]:
    conn = get_conn()
    try:
        return conn.execute(
            """SELECT source,
                      COUNT(*) AS total,
                      SUM(CASE WHEN tagged_at IS NOT NULL THEN 1 ELSE 0 END) AS tagged
               FROM problems GROUP BY source"""
        ).fetchall()
    finally:
        conn.close()
