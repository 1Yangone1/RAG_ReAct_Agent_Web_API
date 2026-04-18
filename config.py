import os

ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY", "")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 默认索引当前项目目录；可通过环境变量 CODE_REPO_PATH 覆盖。
CODE_REPO_PATH = os.getenv("CODE_REPO_PATH", BASE_DIR)
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", os.path.join(BASE_DIR, "chroma_db_zhipu"))