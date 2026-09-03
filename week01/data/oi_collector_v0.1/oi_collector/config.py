"""全局配置：所有可调参数集中在这里。

学习点：项目里把"可能会变的东西"集中到配置文件，是工程化的第一步。
"""
import os
from pathlib import Path

# 项目根目录 & 数据目录（Path 比手写字符串路径更跨平台，Windows/Mac 都能跑）
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "oi.db"

# ===== 礼貌爬取设置（合规红线，不要调小）=====
REQUEST_DELAY = 2.0      # 任意两次请求之间至少间隔 2 秒
REQUEST_TIMEOUT = 15     # 单次请求超时（秒）
MAX_RETRIES = 3          # 失败重试次数
# UA 里标明身份和用途，是爬虫的基本礼仪
USER_AGENT = "oi-collector/0.1 (personal teaching use; Python requests)"

# ===== LLM 配置（OpenAI 兼容接口：DeepSeek / 通义千问 / OpenAI 均可）=====
# 不配置则自动跳过 LLM 标注功能，采集和存储不受影响。
# Windows 设置环境变量：set LLM_API_KEY=sk-xxx
# Mac/Linux：export LLM_API_KEY=sk-xxx
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")
