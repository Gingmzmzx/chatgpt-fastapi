from fastapi import FastAPI, Request, HTTPException, status
import uvicorn, sys, secrets, requests, json, os, asyncio, traceback
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from revChatGPT.revChatGPT import Chatbot

with open("data.json", "r") as f:
    data = json.loads(f.read())

try:
    chatbot = Chatbot(data.get("chatgpt"), conversation_id=None)
except Exception as e:
    print(f"启动ChatGPT失败，请检查配置\n{traceback.format_exc()}")

description = '''
## ChatGPT API Made By [ChatGPT](https://github.com/acheong08/ChatGPT) and FastAPI
'''
app = FastAPI(
    title="ChatGPT API",
    description=description,
    version="1.0.0",
    contact={
        "name": "xzyStudio",
        "url": "https://xzy.center",
        "email": "gingmzmzx@gmail.com",
    },
)
# 初始化 slowapi，注册进 fastapi
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许访问的源
    allow_credentials=True,  # 支持 cookie
    allow_methods=["*"],  # 允许使用的请求方法
    allow_headers=["*"]  # 允许携带的 Headers
)

def checkPassword(password):
    current_password_bytes = password.encode("utf8")
    correct_password_bytes = bytes(data.get("token"), encoding="utf-8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not is_correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    
@app.get("/chat")
# @limiter.limit("12/minute")
async def chat(token:str, message:str):
    checkPassword(token)
    message = chatbot.get_chat_response(message).get('message')
    return message

if __name__ == '__main__':
    uvicorn.run(app="test:app",  host="0.0.0.0", port=int(sys.argv[1]), reload=True)
