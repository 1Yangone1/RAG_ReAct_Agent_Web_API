import os
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from embeddings import get_embedding_function

def read_text_file_safely(file_path):
    """尽量安全地读取文本文件，遇到二进制或编码问题时返回None。"""
    # 先按二进制读取，避免 text 模式下直接抛 UnicodeDecodeError
    with open(file_path, "rb") as f:
        raw = f.read()

    # 简单判断二进制文件（包含空字节通常是二进制）
    if b"\x00" in raw:
        return None

    # 常见编码依次尝试
    for enc in ("utf-8", "utf-8-sig", "gbk", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue

    return None

def index_code_repo(repo_path, collection_name="code_knowledge"):
    """将代码仓库的所有文件分块并索引到Chroma"""
    # 优先使用智谱 Embedding；未配置 key 时回退到本地 sentence-transformers
    from config import ZHIPUAI_API_KEY, CHROMA_DB_PATH
    embedding_fn = get_embedding_function(ZHIPUAI_API_KEY, use_local=True)
    
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_fn
    )
    
    # 遍历所有文件
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    excluded_dirs = {
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "env",
        "chroma_db",
        "chroma_db_zhipu",
    }
    for root, dirs, files in os.walk(repo_path):
        # 原地过滤目录，防止继续向下遍历。
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        for file in files:
            if file.endswith(('.py', '.md', '.txt')):  # 只索引这些类型
                file_path = os.path.join(root, file)
                content = read_text_file_safely(file_path)
                if content is None:
                    print(f"跳过无法解码或疑似二进制文件: {file_path}")
                    continue
                chunks = text_splitter.split_text(content)
                # 为每个块生成元数据
                for i, chunk in enumerate(chunks):
                    collection.add(
                        documents=[chunk],
                        metadatas=[{"source": file_path, "chunk": i}],
                        ids=[f"{file_path}_{i}"]
                    )
    print(f"索引完成，共添加 {collection.count()} 个块")

if __name__ == "__main__":
    # 测试索引
    from config import CODE_REPO_PATH
    index_code_repo(CODE_REPO_PATH)