"""
Azure AI Foundry Client
Wrapper for Azure OpenAI operations using the openai library
"""
from typing import Optional, List
from openai import AsyncAzureOpenAI

from app.core.config import settings


class AzureAIFoundryClient:
    """Client for Azure OpenAI operations"""
    
    _instance: Optional["AzureAIFoundryClient"] = None
    
    def __init__(self):
        self.endpoint = settings.AZURE_OPENAI_ENDPOINT.rstrip('/')
        self.api_key = settings.AZURE_OPENAI_API_KEY
        self.deployment = settings.AZURE_OPENAI_DEPLOYMENT
        self.api_version = settings.AZURE_OPENAI_API_VERSION
        self._client = None
    
    @classmethod
    def get_instance(cls) -> "AzureAIFoundryClient":
        """Singleton pattern for client"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @property
    def client(self) -> AsyncAzureOpenAI:
        """Get or create OpenAI client"""
        if self._client is None:
            self._client = AsyncAzureOpenAI(
                azure_endpoint=self.endpoint,
                api_key=self.api_key,
                api_version=self.api_version
            )
        return self._client
    
    async def chat_completion(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Get chat completion from Azure OpenAI"""
        try:
            # Convert to OpenAI message format if needed
            formatted_messages = []
            for msg in messages:
                if hasattr(msg, 'content'):
                    # It's a Message object
                    role = 'system' if 'System' in type(msg).__name__ else 'user'
                    formatted_messages.append({"role": role, "content": msg.content})
                else:
                    # Already a dict
                    formatted_messages.append(msg)
            
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Azure OpenAI error: {str(e)}")
    
    async def simple_chat(self, user_message: str, system_message: str = None) -> str:
        """Simple chat interface"""
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": user_message})
        
        return await self.chat_completion(messages)


def get_ai_client() -> AzureAIFoundryClient:
    """Dependency injection for AI client"""
    return AzureAIFoundryClient.get_instance()
