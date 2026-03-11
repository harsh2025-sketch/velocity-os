"""
LLM Client: Interface to Ollama / Local Model
"""
from typing import Optional

class LLMClient:
    def __init__(self, model: str = "ollama", endpoint: str = "http://localhost:11434"):
        self.model = model
        self.endpoint = endpoint
    
    def query(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Send query to LLM"""
        # Stub: Replace with actual Ollama API call
        return f"Response from {self.model}"
    
    def stream_query(self, prompt: str):
        """Stream response from LLM"""
        # Stub: Replace with streaming API call
        pass
