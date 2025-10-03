# app/providers/xinghuo_provider.py

import httpx
import json
import uuid
import time
import traceback
import base64
from typing import Dict, Any, AsyncGenerator, Union, List

from app.providers.base import BaseProvider
from app.core.config import settings

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class XinghuoProvider(BaseProvider):
    """
    讯飞星火 Provider (v1.0)
    - 基于 multipart/form-data 请求
    - 实现 Base64 增量流解析
    """

    def __init__(self):
        if not settings.XINGHUO_COOKIE:
            raise ValueError("讯飞星火的 Cookie (XINGHUO_COOKIE) 未在 .env 文件中配置。")
        if not settings.GT_TOKEN:
            raise ValueError("讯飞星火的 GtToken (GT_TOKEN) 未在 .env 文件中配置。")

    async def chat_completion(self, request_data: Dict[str, Any]) -> AsyncGenerator[str, None]:
        # 星火总是流式的，所以我们直接返回生成器
        return self._stream_generator(request_data)

    def _prepare_headers(self) -> Dict[str, str]:
        """准备请求头"""
        return {
            'Accept': 'text/event-stream',
            'Cookie': settings.XINGHUO_COOKIE,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Origin': 'https://xinghuo.xfyun.cn',
            'Referer': 'https://xinghuo.xfyun.cn/desk',
        }

    def _prepare_payload(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """准备 multipart/form-data 请求体"""
        messages: List[Dict[str, Any]] = request_data.get("messages", [])
        user_prompt = messages[-1].get("content", "你好")

        # 注意：chatId 和 GtToken 是关键。chatId 决定了对话上下文。
        # GtToken 是安全令牌，可能会过期。
        return {
            "fd": "775510",
            "isBot": "0",
            "clientType": "",
            "text": user_prompt,
            "capabilities": "deep_think",
            "chatId": "985818485", # 使用抓包获取的 chatId
            "GtToken": settings.GT_TOKEN,
        }

    async def _stream_generator(self, request_data: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """处理流式任务并解析 Base64 编码的响应"""
        headers = self._prepare_headers()
        payload = self._prepare_payload(request_data)
        model_name = request_data.get("model", "spark-3.5-max")
        chat_id = f"chatcmpl-{uuid.uuid4().hex}"
        is_first_chunk = True
        
        url = "https://xinghuo.xfyun.cn/iflygpt-chat/u/chat_message/chat"
        
        logger.info(f"正在向星火服务发送流式请求: {url}")

        try:
            async with httpx.AsyncClient(timeout=180) as client:
                async with client.stream("POST", url, headers=headers, data=payload) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if not line.startswith('data:'):
                            continue
                        
                        raw_data = line.strip()[len('data:'):]

                        # 检查并跳过特殊标记
                        if "<end>" in raw_data or "<sid>" in raw_data:
                            continue
                        
                        # 跳过元数据信息
                        if raw_data.startswith('PGRlZXBfeDE+'):
                            continue

                        try:
                            # 解码 Base64 内容块
                            decoded_bytes = base64.b64decode(raw_data)
                            delta_content = decoded_bytes.decode('utf-8')

                            if not delta_content:
                                continue

                            # 第一次发送角色信息
                            if is_first_chunk:
                                role_chunk = {
                                    "id": chat_id, "object": "chat.completion.chunk", "created": int(time.time()), "model": model_name,
                                    "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}]
                                }
                                yield f"data: {json.dumps(role_chunk, ensure_ascii=False)}\n\n"
                                is_first_chunk = False

                            # 发送增量内容
                            openai_chunk = {
                                "id": chat_id, "object": "chat.completion.chunk", "created": int(time.time()), "model": model_name,
                                "choices": [{"index": 0, "delta": {"content": delta_content}, "finish_reason": None}]
                            }
                            yield f"data: {json.dumps(openai_chunk, ensure_ascii=False)}\n\n"

                        except Exception:
                            # 忽略无法解析的行
                            logger.warning(f"无法解析的 Base64 数据块: {raw_data}")
                            continue
            
            # 流结束，发送终止块
            final_chunk = {
                "id": chat_id, "object": "chat.completion.chunk", "created": int(time.time()), "model": model_name,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
            }
            yield f"data: {json.dumps(final_chunk, ensure_ascii=False)}\n\n"
        
        except Exception as e:
            logger.error(f"流式生成器发生错误: {e}")
            traceback.print_exc()
        
        finally:
            logger.info("流式传输结束。")
            yield "data: [DONE]\n\n"