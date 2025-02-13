from typing import AsyncGenerator, Dict, List, Optional
import anthropic
from anthropic.types import Message

from ...utils.logger import logger
from .stream import MessageStream
from ..constants import (
    MODEL_NAME,
    DEFAULT_TEMPERATURE,
    MAX_TOKENS,
    MessageRole,
)

class ClaudeModel:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key is required")
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        
    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> AsyncGenerator[str, None]:
        """Stream a chat response from Claude"""
        try:
            # Create the messages request with system prompt as a parameter
            request = {
                "model": MODEL_NAME,
                "messages": [{"role": m["role"], "content": m["content"]} for m in messages],
                "temperature": temperature,
                "max_tokens": MAX_TOKENS,
                "stream": True
            }
            
            # Add system prompt if provided
            if system_prompt:
                request["system"] = system_prompt
            
            stream = await self.client.messages.create(**request)
            
            message_stream = MessageStream()
            async for chunk in stream:
                if chunk.type == "content_block_delta":
                    yield chunk.delta.text
                    message_stream.add_chunk(chunk.delta.text)
            
            logger.debug("Chat stream completed")
            
        except Exception as e:
            logger.error(f"Error in chat stream: {str(e)}")
            raise

    def _format_messages(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
    ) -> List[Message]:
        """Format messages for Claude API"""
        # Only include user/assistant messages, system prompt is handled separately
        return [
            {"role": m["role"], "content": m["content"]} 
            for m in messages 
            if m["role"] in [MessageRole.USER, MessageRole.ASSISTANT]
        ] 