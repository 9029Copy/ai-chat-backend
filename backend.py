# backend.py
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import PlainTextResponse
import uvicorn
import httpx
import json
import os
from collections import deque, defaultdict
import yaml

# -------------------------------------------------
# 读取统一配置文件
# -------------------------------------------------
CONFIG_FILE = "config.yaml"
with open(CONFIG_FILE, encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

VALID_KEYS  = set(cfg["api_keys"])
AI_SCHEME   = cfg["ai_api_scheme"]
AI_HOST     = cfg["ai_api_host"]
AI_PORT     = cfg["ai_api_port"]
AI_PATH     = cfg["ai_api_path"]
AI_TOKEN    = cfg["ai_api_token"]
MODEL       = cfg["ai_model"]
MAX_HISTORY = cfg.get("max_history", 5)

# -------------------------------------------------
# 会话存储：key -> 双端队列
# -------------------------------------------------
sessions: dict[str, deque] = defaultdict(lambda: deque(maxlen=MAX_HISTORY))

# -------------------------------------------------
# FastAPI 实例 & 鉴权
# -------------------------------------------------
app = FastAPI()
security = HTTPBearer(auto_error=False)   # 允许空 header

def verify_key(creds: HTTPAuthorizationCredentials = Depends(security)):
    if not creds or creds.credentials not in VALID_KEYS:
        raise HTTPException(status_code=401, detail="Invalid key")
    return creds.credentials   # 返回 key，用于区分会话

# -------------------------------------------------
# /chat 端点：纯文本输入输出
# -------------------------------------------------
@app.post("/chat", response_class=PlainTextResponse)
async def chat(request: Request, key: str = Depends(verify_key)):
    # 读取原始文本
    body = await request.body()
    question = body.decode().strip()
    if not question:
        raise HTTPException(status_code=400, detail="Empty question")

    # 拼装带上下文的 messages
    history = sessions[key]
    messages = [{"role": role, "content": content} for role, content in history]
    messages.append({"role": "user", "content": question})

    headers = {
        "Authorization": f"Bearer {AI_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"model": MODEL, "messages": messages}

    # 调用上游大模型
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"https://{AI_HOST}{AI_PATH}",
                              json=payload, headers=headers)
        if r.status_code != 200:
            raise HTTPException(status_code=502, detail="Upstream error")
        answer = r.json()["choices"][0]["message"]["content"]

    # 更新会话历史
    history.append(("user", question))
    history.append(("assistant", answer))

    return answer     # FastAPI 自动按 text/plain 返回

# -------------------------------------------------
# 启动入口
# -------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8000)