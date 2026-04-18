# main.py — 命令行入口，使用 ReAct Agent
from assistant import get_retriever_cached
from react_agent import react_agent

def main():
    retriever = get_retriever_cached()
    print("代码库助手已启动（ReAct），输入问题（输入 exit 退出）：")
    
    history = []  # 存储历史对话
    
    while True:
        query = input("\n> ")
        if query.lower() == "exit":
            break
        
        docs, metas = retriever(query)
        if not docs:
            docs, metas = [], []

        # 生成答案，传入真实历史（上一轮 assistant 内容来自模型真实输出）
        answer = react_agent(query, (docs, metas), history)
        print("\n回答：", answer)

        # 将本轮真实问答加入历史，避免后续指代消解出现“伪造 assistant”问题。
        history.extend(
            [
                {"role": "user", "content": query},
                {"role": "assistant", "content": answer},
            ]
        )
        
        # 可选：限制历史长度，避免 token 过多
        if len(history) > 10:  # 保留最近 10 条（5轮）
            history = history[-10:]

if __name__ == "__main__":
    main()