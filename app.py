# app.py — FastAPI 聊天接口
import os
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from assistant import get_retriever_cached
from react_agent import react_agent

@asynccontextmanager
async def lifespan(app: FastAPI):
    get_retriever_cached()
    yield


app = FastAPI(title="代码库 RAG + ReAct Agent", lifespan=lifespan)


# 根路径返回前端页面
@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


# 挂载静态文件（CSS/JS等，如果有的话）
app.mount("/static", StaticFiles(directory="static"), name="static")


class ChatMessage(BaseModel):
    role: str = Field(..., description="user 或 assistant")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., description="用户当前问题")
    history: Optional[List[ChatMessage]] = Field(default=None, description="可选多轮历史")


class ChatResponse(BaseModel):
    answer: str


@app.get("/health")
def health():
    return {"status": "ok", "zhipu_configured": bool(os.getenv("ZHIPUAI_API_KEY"))}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not os.getenv("ZHIPUAI_API_KEY"):
        raise HTTPException(status_code=500, detail="未设置环境变量 ZHIPUAI_API_KEY")
    retriever = get_retriever_cached()
    docs, metas = retriever(req.message)
    if not docs:
        docs, metas = [], []
    hist = None
    if req.history:
        hist = [{"role": m.role, "content": m.content} for m in req.history]
    answer = react_agent(req.message, (docs, metas), hist, verbose=False)
    return ChatResponse(answer=answer)