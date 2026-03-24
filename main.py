from indexer import index_code_repo
from retriever import get_retriever
from generator import generate_answer
from config import CODE_REPO_PATH
import os

def main():
    # 如果还没有索引，先索引（也可以注释掉，手动运行 indexer.py）
    if not os.path.exists("./chroma_db"):
        print("首次运行，正在索引代码库...")
        index_code_repo(CODE_REPO_PATH)
    
    retriever = get_retriever()
    print("代码库助手已启动，输入问题（输入 exit 退出）：")
    while True:
        query = input("\n> ")
        if query.lower() == "exit":
            break
        docs, metas = retriever(query)
        if not docs:
            print("未找到相关代码片段。")
            continue
        answer = generate_answer(query, (docs, metas))
        print("\n回答：", answer)

if __name__ == "__main__":
    main()