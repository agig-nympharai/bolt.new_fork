from typing import List

class MessageStream:
    """Handles streaming message chunks and reconstruction"""
    
    def __init__(self):
        self._chunks: List[str] = []
        self._complete = False
    
    def add_chunk(self, chunk: str):
        """Add a new chunk to the message"""
        self._chunks.append(chunk)
    
    def get_full_message(self) -> str:
        """Get the complete message"""
        return "".join(self._chunks)
    
    def mark_complete(self):
        """Mark the stream as complete"""
        self._complete = True
    
    @property
    def is_complete(self) -> bool:
        return self._complete 