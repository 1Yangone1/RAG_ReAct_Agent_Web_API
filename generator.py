import os
import json
from zhipuai import ZhipuAI
from tools import list_python_files, read_file, tools

def _build_context(retrieved_docs):
    return "\n\n".join(
        [f"文件 {meta['source']} 片段：\n{doc}" for doc, meta in zip(*retrieved_docs)]
    )

def call_tool(tool_call):
    """执行工具调用并返回结果"""
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    if name == "list_python_files":
        return list_python_files(**args)
    elif name == "read_file":
        return read_file(**args)
    else:
        return f"未知工具：{name}"

def answer_with_tools(query, retrieved_docs, history=None):
    """
    支持工具调用的回答流程
    """
    client = ZhipuAI(api_key=os.getenv("ZHIPUAI_API_KEY"))
    
    # 构建系统提示
    system_prompt = "你是一个代码库助手，可以使用工具来帮助回答用户问题。"
    
    # 构建上下文（代码片段）
    context = _build_context(retrieved_docs)
    
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    # 当前用户问题
    user_content = f"用户问题：{query}\n\n相关代码片段：\n{context}"
    messages.append({"role": "user", "content": user_content})
    
    # 第一次调用，允许工具
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    # 处理工具调用
    message = response.choices[0].message
    if message.tool_calls:
        # 有工具调用，执行工具并将结果返回
        assistant_tool_call_msg = {
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in message.tool_calls
            ],
        }
        messages.append(assistant_tool_call_msg)
        for tool_call in message.tool_calls:
            tool_result = call_tool(tool_call)
            # 将工具结果作为新消息加入
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(tool_result)
            })
        # 再次调用大模型，使用工具结果生成最终答案
        final_response = client.chat.completions.create(
            model="glm-4-flash",
            messages=messages
        )
        return final_response.choices[0].message.content
    else:
        # 无工具调用，直接返回
        return message.content

def generate_answer(query, retrieved_docs, history=None):
    """
    :param query: 当前用户问题
    :param retrieved_docs: 检索到的文档列表 (documents, metadatas)
    :param history: 历史对话列表，每个元素为 {"role": "user"/"assistant", "content": ...}
    """
    client = ZhipuAI(api_key=os.getenv("ZHIPUAI_API_KEY"))
    
    # 构建上下文（检索到的代码片段）
    context = _build_context(retrieved_docs)
    
    system_prompt = "你是一个代码库助手。根据以下从代码仓库中检索到的相关片段，回答用户的问题。如果找不到相关信息，请说明。"
    
    # 构建消息列表：系统提示 + 历史消息（如果有） + 当前用户问题（带检索上下文）
    messages = [{"role": "system", "content": system_prompt}]
    
    if history:
        # 将历史消息加入（注意：历史中已经包含了之前的用户问题和助手回答）
        messages.extend(history)
    
    # 当前用户消息，携带检索到的上下文
    user_content = f"用户问题：{query}\n\n相关代码片段：\n{context}"
    messages.append({"role": "user", "content": user_content})
    
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=messages,
        temperature=0.3
    )
    return response.choices[0].message.content