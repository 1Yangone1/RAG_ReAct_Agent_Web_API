# assistant.py — CLI / Web 共用的索引与检索入口
import os

from config import CHROMA_DB_PATH, CODE_REPO_PATH
from indexer import index_code_repo
from retriever import get_retriever

_retriever = None


def ensure_indexed():
    if not os.path.exists(CHROMA_DB_PATH):
        print("首次运行，正在索引代码库...")
        index_code_repo(CODE_REPO_PATH)


def get_retriever_cached():
    global _retriever
    if _retriever is None:
        ensure_indexed()
        _retriever = get_retriever()
    return _retriever
