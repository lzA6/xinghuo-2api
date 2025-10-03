# main.py (Xinghuo-2api)

import traceback
import time
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.responses import StreamingResponse, JSONResponse

from app.core.config import settings
from app.providers.xinghuo_provider import XinghuoProvider

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.DESCRIPTION
)

# 初始化 Provider
provider = XinghuoProvider()


# --- 认证依赖项 ---
async def verify_api_key(authorization: Optional[str] = Header(None)):
    """
    检查 API 密钥的依赖项。
    """
    if not settings.API_MASTER_KEY:
        return

    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Missing Authorization header.",
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme. Use 'Bearer <your_api_key>'.",
        )
    
    if token != settings.API_MASTER_KEY:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Invalid API Key.",
        )


# --- 核心聊天接口 ---
@app.post("/v1/chat/completions", dependencies=[Depends(verify_api_key)])
async def chat_completions(request: Request):
    """
    核心路由：所有聊天请求都交给 Provider 处理。
    """
    try:
        request_data = await request.json()
        response_generator = await provider.chat_completion(request_data)
        
        is_stream = request_data.get("stream", False)
        if is_stream:
            return StreamingResponse(response_generator, media_type="text/event-stream")
        else:
            # 如果需要支持非流式，需要在这里聚合流式响应
            # If non-streaming support is needed, the streaming response needs to be aggregated here.
            full_response = ""
            async for chunk in response_generator:
                # 解析 chunk 并累加内容
                # Parse the chunk and accumulate the content
                pass # 实现聚合逻辑
            return JSONResponse({"content": full_response}) # 返回聚合后的内容
            
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# --- 模型列表接口 ---
@app.get("/v1/models", dependencies=[Depends(verify_api_key)])
async def list_models():
    """
    返回兼容OpenAI格式的模型列表。
    """
    model_names: List[str] = settings.SUPPORTED_MODELS
    
    model_data: List[Dict[str, Any]] = []
    for name in model_names:
        model_data.append({
            "id": name,
            "object": "model",
            "created": int(time.time()),
            "owned_by": "system"
        })
        
    return {
        "object": "list",
        "data": model_data
    }


# --- 根路由 ---
@app.get("/")
def root():
    """根路由，提供服务基本信息。"""
    return {"message": f"Welcome to {settings.APP_NAME}", "version": settings.APP_VERSION}