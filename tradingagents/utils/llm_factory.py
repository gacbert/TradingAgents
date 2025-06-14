import os
from typing import Any

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_deepseek import ChatDeepSeek
from langchain_core.language_models.chat_models import BaseChatModel


DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"


def create_chat_llm(model_name: str, **kwargs: Any) -> BaseChatModel:
    """Create a chat model instance based on the model name."""
    temperature = kwargs.pop("temperature", 0.7)

    if model_name.lower().startswith("gemini"):
        # Google Gemini models
        return ChatGoogleGenerativeAI(model=model_name, temperature=temperature, **kwargs)
    if model_name.lower().startswith("deepseek"):
        # DeepSeek models
        return ChatDeepSeek(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            api_base=DEEPSEEK_BASE_URL,
            **kwargs,
        )
    # Default to OpenAI models
    return ChatOpenAI(model=model_name, temperature=temperature, **kwargs)
