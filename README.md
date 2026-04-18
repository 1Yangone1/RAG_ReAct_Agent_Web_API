# RAG Code Assistant

一个面向本地代码库的问答助手，结合 RAG 检索与 ReAct 工具调用。  
支持命令行对话和 FastAPI Web API 两种使用方式。

## 功能特性

- 索引 `py/md/txt` 文件到 Chroma 向量库
- 语义检索相关代码片段（RAG）
- ReAct 循环支持工具调用（列文件、读文件）
- 多轮历史对话（`user/assistant` 真实答案串联）
- 提供 Web API：`/chat`、`/health`，并可挂载静态页面

## 项目结构

- `main.py`: CLI 入口
- `app.py`: FastAPI 服务入口
- `react_agent.py`: ReAct 推理循环
- `prompts.py`: ReAct 提示词模板
- `indexer.py`: 代码索引构建
- `retriever.py`: 向量检索器
- `embeddings.py`: 本地 / 智谱 embedding 实现
- `tools.py`: Agent 可调用工具

## 环境准备（Windows PowerShell）

1. 创建虚拟环境
   - `python -m venv .venv`
2. 激活虚拟环境
   - `.\\.venv\\Scripts\\activate`
3. 安装依赖
   - `pip install -r requirements.txt`
4. 设置智谱 API Key（可选，未设置时默认走本地 embedding）
   - `$env:ZHIPUAI_API_KEY="你的Key"`

## 配置说明

`config.py` 支持环境变量覆盖：

- `CODE_REPO_PATH`: 要索引的代码目录（默认当前项目目录）
- `CHROMA_DB_PATH`: 向量库目录（默认 `./chroma_db_zhipu`）

示例：

```powershell
$env:CODE_REPO_PATH="D:\\your_repo"
$env:CHROMA_DB_PATH="D:\\your_repo\\chroma_db_zhipu"
```

## 运行方式

### 1) 命令行模式

```powershell
python main.py
```

### 2) Web API 模式

```powershell
uvicorn app:app --reload
```

启动后可访问：

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

## API 示例

`POST /chat`

请求体：

```json
{
  "message": "请列出项目中的所有 Python 文件",
  "history": []
}
```

响应体：

```json
{
  "answer": "..."
}
```

## 常见问题

- 首次运行较慢：需要构建索引和加载 embedding 模型
- 若网络受限，本地模型可能重试下载；可提前缓存模型
- `ZHIPUAI_API_KEY` 未配置时，LLM 调用会失败（embedding 可本地）