"""LLM 增强：让大模型给题目打"知识点标签"、建议"适合年级"。

这是整个项目里 AI 大模型的切入点，也是 Q2 做 RAG 备课机器人的预演：
- 用 OpenAI 兼容接口（DeepSeek 最便宜，几块钱能标注几千题）；
- 要求模型输出 JSON，程序再解析——结构化输出是 LLM 应用的基本功；
- 任何失败都只警告、不中断：AI 是增强，不是依赖。
"""
import json
import logging
from typing import Optional, Dict, List

import requests

import config

log = logging.getLogger("oi.llm")

PROMPT_TEMPLATE = """你是信息学奥赛教练。下面是一道编程题的信息：
标题：{title}
平台标签：{tags}
难度评分：{difficulty}

请输出 JSON（不要输出任何其他内容）：
{{"knowledge_tags": ["最多5个中文知识点标签，如：动态规划、贪心、模拟"], "grade": "适合学段：4-5年级/6年级/初中/高中+"}}
"""


def tag_one(title: str, tags: List[str], difficulty: Optional[int]) -> Optional[Dict]:
    """标注单题。失败或未配置 Key 时返回 None。"""
    if not config.LLM_API_KEY:
        return None

    prompt = PROMPT_TEMPLATE.format(
        title=title,
        tags=", ".join(tags) if tags else "无",
        difficulty=difficulty if difficulty is not None else "未知",
    )
    try:
        resp = requests.post(
            f"{config.LLM_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {config.LLM_API_KEY}"},
            json={
                "model": config.LLM_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
            },
            timeout=30,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        result = json.loads(content)
        return {
            "knowledge_tags": result.get("knowledge_tags", []),
            "grade": result.get("grade", ""),
        }
    except Exception as e:  # LLM 失败不应影响主流程
        log.warning("LLM 标注失败（%s）：%s", title[:20], e)
        return None
