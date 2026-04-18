# tools.py
import os
import glob

def list_python_files(path="."):
    """列出指定路径下的所有 Python 文件（相对路径）"""
    files = glob.glob(os.path.join(path, "**", "*.py"), recursive=True)
    # 过滤掉虚拟环境目录
    files = [f for f in files if "venv" not in f and "__pycache__" not in f]
    return "\n".join(files) if files else "未找到 Python 文件。"

def read_file(file_path):
    """读取指定文件的内容（前 2000 字符）"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read(2000)
        return content
    except Exception as e:
        return f"读取文件失败：{e}"

# 工具描述（供大模型理解）
tools = [
    {
        "type": "function",
        "function": {
            "name": "list_python_files",
            "description": "列出当前目录下所有 Python 文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "要搜索的目录路径，默认为当前目录",
                        "default": "."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取指定文件的内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "要读取的文件路径"
                    }
                },
                "required": ["file_path"]
            }
        }
    }
]