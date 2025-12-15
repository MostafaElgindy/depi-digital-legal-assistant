"""
LLM Service Module
===================
Large Language Model service using Groq Llama-3.3-70B-Versatile.
Uses langchain-groq library for integration.
"""

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Optional, List, Dict, Any
import time

from core.config import get_settings, SYSTEM_PROMPT_TEMPLATE, USER_PROMPT_TEMPLATE
from models.document import LLMResponse


class LLMService:
    """
    LLM service for communicating with Groq API.
    Uses Llama-3.3-70B-Versatile model.
    """
    
    def __init__(self):
        """
        Initialize LLM service.
        Reads settings from Environment Variables.
        """
        self._settings = get_settings()
        self._llm: Optional[ChatGroq] = None
        self._initialize_llm()
    
    def _initialize_llm(self) -> None:
        """
        Create ChatGroq object with specified settings.
        """
        self._llm = ChatGroq(
            api_key=self._settings.groq_api_key,
            model_name=self._settings.llm_model_name,
            temperature=self._settings.llm_temperature,
            max_tokens=self._settings.llm_max_tokens,
        )
    
    @property
    def model_name(self) -> str:
        """Get model name"""
        return self._settings.llm_model_name
    
    async def generate_response(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        """
        Generate response from LLM model.
        
        Args:
            query: User question
            context: Context retrieved from documents
            system_prompt: System message (optional)
        
        Returns:
            LLMResponse: Object containing answer and metadata
        """
        start_time = time.time()
        
        # Use prompts defined in config
        if system_prompt is None:
            system_prompt = SYSTEM_PROMPT_TEMPLATE
        
        user_message = USER_PROMPT_TEMPLATE.format(
            context=context,
            query=query
        )
        
        # Create messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        # Call model
        response = await self._llm.ainvoke(messages)
        
        generation_time = time.time() - start_time
        
        # Extract token count if available
        tokens_used = None
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            tokens_used = response.usage_metadata.get('total_tokens')
        
        return LLMResponse(
            answer=response.content,
            model_name=self.model_name,
            tokens_used=tokens_used,
            generation_time=round(generation_time, 3)
        )
    
    def generate_response_sync(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        """
        Generate response synchronously.
        
        Args:
            query: User question
            context: Retrieved context
            system_prompt: System message (optional)
        
        Returns:
            LLMResponse: Response object
        """
        start_time = time.time()
        
        if system_prompt is None:
            system_prompt = SYSTEM_PROMPT_TEMPLATE
        
        user_message = USER_PROMPT_TEMPLATE.format(
            context=context,
            query=query
        )
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        response = self._llm.invoke(messages)
        
        generation_time = time.time() - start_time
        
        tokens_used = None
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            tokens_used = response.usage_metadata.get('total_tokens')
        
        return LLMResponse(
            answer=response.content,
            model_name=self.model_name,
            tokens_used=tokens_used,
            generation_time=round(generation_time, 3)
        )
    
    def health_check(self) -> bool:
        """
        Check Groq API connection health.
        
        Returns:
            bool: True if connection is healthy
        """
        try:
            messages = [
                HumanMessage(content="مرحبا")
            ]
            response = self._llm.invoke(messages)
            return len(response.content) > 0
        except Exception:
            return False


# ==================== Dependency Injection ====================

_llm_service_instance: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """
    Get LLM service instance (Singleton pattern).
    Used with FastAPI Dependency Injection.
    
    Returns:
        LLMService: LLM service instance
    """
    global _llm_service_instance
    
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    
    return _llm_service_instance


def reset_llm_service() -> None:
    """
    Reset LLM service.
    Useful for tests or updating settings.
    """
    global _llm_service_instance
    _llm_service_instance = None
