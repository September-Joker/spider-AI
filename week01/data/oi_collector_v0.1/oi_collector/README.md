# 信奥题库采集器（oi-collector）

教学练手项目 v0.1 —— 12 个月成长路线图 · Q1 第一个实战项目。

采集 Codeforces / AtCoder 题目，清洗存入本地数据库，可用大模型自动标注知识点和适合年级。
既是备课工具，也是你 GitHub 上的第一个工程化作品集。

## 快速开始

```bash
# 1. 进入项目目录
cd oi_collector

# 2. （建议）创建虚拟环境
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 跑起来
python main.py fetch --source codeforces --limit 20
python main.py fetch --source atcoder --limit 20
python main.py list --source codeforces
python main.py stats
```

## LLM 标注（可选，不配 Key 不影响采集）

```bash
# Windows
set LLM_API_KEY=sk-你的key
# Mac/Linux
export LLM_API_KEY="sk-你的key"

# DeepSeek 用户默认即可；用其他 OpenAI 兼容接口时设置：
set LLM_BASE_URL=https://api.openai.com/v1
set LLM_MODEL=gpt-4o-mini

python main.py tag --limit 10
```

## 项目结构

```
oi_collector/
├── main.py                 # 命令行入口（fetch/tag/list/stats）
├── config.py               # 全局配置：限速、数据库路径、LLM Key
├── requirements.txt
├── data/                   # 运行后生成 oi.db（SQLite 数据库）
├── collector/              # 采集层
│   ├── base.py             #   基类：限速 + 指数退避重试
│   ├── codeforces.py       #   Codeforces 官方 API（合法稳定）
│   ├── atcoder.py          #   AtCoder 社区 API（第三方接口适配）
│   └── luogu.py            #   洛谷：有 WAF，Playwright 进阶练习，默认未启用
├── pipeline/               # 数据管线
│   ├── clean.py            #   清洗：坏数据丢弃、标签标准化
│   └── storage.py          #   SQLite 存储 + upsert 去重
└── llm/
    └── tagger.py           # LLM 打知识点标签 + 建议年级
```

## 数据从哪来，到哪去

```
Codeforces API ─┐
                ├─> collector（限速/重试）─> clean（清洗过滤）
AtCoder API ─────┘                                     │
                                                      ▼
                              SQLite（oi.db，按 来源+题号 去重）
                                                      │
                                          llm.tagger（大模型标注）
                                                      ▼
                                         知识点标签 / 适合年级
```

## 扩展练习（按顺序做，每做一个 commit 一次）

1. **新增数据源**：照着 `atcoder.py` 写一个牛客采集器注册进 `main.py`；把 `luogu.py` 用 Playwright 改造后启用
2. **异步提速**：把 `base.py` 的同步 requests 改成 `aiohttp + asyncio`，1000 条数据体验差异
3. **定时任务**：用系统计划任务（Windows 任务计划程序 / cron）每周一自动 `fetch`
4. **导出工具**：加 `python main.py export --keyword 动态规划`，按标签筛题导出 Markdown 试卷
5. **Web 界面**：用 Streamlit 给题库加个搜索页面，能按知识点/难度筛题——这是 Q2 AI 备课机器人的雏形
6. **反爬第一课**：用 Playwright 打开一个 JS 渲染的网站（先在自己练习页面上做，尊重 robots.txt）
7. **RAG 预演**：把题目标题+标签喂给向量库，实现"我想讲贪心，给我 10 道合适的题"自然语言检索

## 合规红线

- 严格遵守目标网站 robots.txt，默认 2 秒/次限速，不要调高并发压垮别人服务器
- 只采集公开数据，不碰需要登录/付费的内容，不收集任何个人信息
- 仅供个人教学和学习使用，不公开传播抓取的原始数据
- LLM 标注结果参考使用，教学判断以你自己为准
