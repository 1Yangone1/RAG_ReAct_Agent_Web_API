# react_agent.py — ReAct 循环（文本协议 + 本地工具执行）
import json
import os
import re
from zhipuai import ZhipuAI

from tools import list_python_files, read_file, tools
from prompts import REACT_PROMPT


def _tool_descriptions_for_prompt():
    lines = []
    for t in tools:
        fn = t["function"]
        name = fn["name"]
        desc = fn.get("description", "")
        params = json.dumps(fn.get("parameters", {}), ensure_ascii=False)
        lines.append(f"- **{name}**: {desc}\n  参数 schema: {params}")
    return "\n".join(lines)


def _build_context(retrieved_docs):
    docs, metas = retrieved_docs
    if not docs:
        return "（向量检索未返回相关片段；请使用工具探索代码库。）"
    return "\n\n".join(
        f"文件 {meta.get('source', '?')} 片段：\n{doc}" for doc, meta in zip(docs, metas)
    )


def execute_action(action_name, action_input):
    """执行动作并返回观察结果（字符串）。"""
    raw = (action_input or "").strip()
    if not raw:
        return "错误：Action Input 为空，请提供 JSON 对象（例如 {{}}）。"
    try:
        args = json.loads(raw)
    except json.JSONDecodeError as e:
        return f"错误：Action Input 不是合法 JSON：{e}"
    if action_name == "list_python_files":
        return str(list_python_files(**args))
    if action_name == "read_file":
        return str(read_file(**args))
    return f"未知动作：{action_name}"


def _extract_final_answer(text):
    if "Final Answer:" not in text:
        return None
    return text.split("Final Answer:", 1)[1].strip()


def parse_react_output(text):
    """
    从模型输出中解析 Thought、Action、Action Input。
    Action Input 支持单行或多行 JSON（从 Action Input: 后到下一个 Thought:/Action:/Final Answer: 之前）。
    """
    thought = None
    action = None
    action_input = None

    m_thought = re.search(
        r"Thought:\s*(.+?)(?=\n\s*(?:Action:|Final Answer:)|\Z)",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if m_thought:
        thought = m_thought.group(1).strip()

    m_action = re.search(r"^Action:\s*(\S+)\s*$", text, flags=re.MULTILINE | re.IGNORECASE)
    if m_action:
        action = m_action.group(1).strip()

    m_ain = re.search(r"Action Input:\s*", text, flags=re.IGNORECASE)
    if m_ain:
        rest = text[m_ain.end() :]
        stop = re.search(
            r"\n\s*(?:Thought:|Action:|Final Answer:)\s*",
            rest,
            flags=re.IGNORECASE,
        )
        if stop:
            rest = rest[: stop.start()]
        action_input = rest.strip()
        if action_input.startswith("```"):
            action_input = re.sub(
                r"^```(?:json)?\s*",
                "",
                action_input,
                flags=re.IGNORECASE,
            ).strip()
            action_input = re.sub(r"\s*```\s*$", "", action_input).strip()

    return thought, action, action_input


def react_agent(query, retrieved_docs, history=None, max_steps=8, verbose=True):
    """
    ReAct 循环：调用智谱模型 → 解析 Action → 执行工具 → 将 Observation 写回对话，直到 Final Answer 或步数上限。
    """
    client = ZhipuAI(api_key=os.getenv("ZHIPUAI_API_KEY"))
    context = _build_context(retrieved_docs)

    if history:
        history_str = "\n".join(f"{msg['role']}: {msg['content']}" for msg in history)
    else:
        history_str = "（无）"

    tool_descriptions = _tool_descriptions_for_prompt()
    prompt = REACT_PROMPT.format(
        tool_descriptions=tool_descriptions,
        query=query,
        context=context,
        history=history_str,
    )
    messages = [{"role": "user", "content": prompt}]

    for step in range(max_steps):
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=messages,
            temperature=0.2,
        )
        output = (response.choices[0].message.content or "").strip()
        if verbose:
            print(f"\n--- ReAct step {step + 1} ---\n{output}\n")

        final = _extract_final_answer(output)
        if final is not None:
            return final

        thought, action, action_input = parse_react_output(output)
        messages.append({"role": "assistant", "content": output})

        if action and action_input is not None:
            observation = execute_action(action, action_input)
            messages.append(
                {
                    "role": "user",
                    "content": f"Observation:\n{observation}\n\n请继续：给出下一组 Thought/Action/Action Input，或给出 Final Answer。",
                }
            )
        else:
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "未能解析有效的 Action 与 Action Input。"
                        "请严格使用格式：Thought: ... 然后 Action: 工具名 然后 Action Input: JSON；"
                        "或给出 Final Answer: ..."
                    ),
                }
            )

    return "未在最大步数内得到 Final Answer；请缩小问题范围或检查 API/工具配置。"
