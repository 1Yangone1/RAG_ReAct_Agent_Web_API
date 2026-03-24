import os
from zhipuai import ZhipuAI

def generate_answer(query, retrieved_docs):
    client = ZhipuAI(api_key=os.getenv("ZHIPUAI_API_KEY"))
    
    # 构建上下文
    context = "\n\n".join([f"文件 {meta['source']} 片段：\n{doc}" for doc, meta in zip(*retrieved_docs)])
    
    system_prompt = "你是一个代码库助手。根据以下从代码仓库中检索到的相关片段，回答用户的问题。如果找不到相关信息，请说明。"
    user_prompt = f"用户问题：{query}\n\n相关代码片段：\n{context}"
    
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content