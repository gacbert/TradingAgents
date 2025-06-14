import os
from typing import Any

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_deepseek import ChatDeepSeek
from langchain_core.language_models.chat_models import BaseChatModel

try:
    from google.api_core.exceptions import NotFound
except Exception:  # pragma: no cover - package may not be installed during docs build
    NotFound = Exception


DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"


def create_chat_llm(model_name: str, **kwargs: Any) -> BaseChatModel:
    """Create a chat model instance based on the model name."""
    temperature = kwargs.pop("temperature", 0.7)

    if model_name.lower().startswith("gemini"):
        # Google Gemini models
        try:
            return ChatGoogleGenerativeAI(
                model=model_name, temperature=temperature, **kwargs
            )
        except NotFound:
            fallback = "gemini-1.5-flash-latest"
            if model_name != fallback:
                print(
                    f"Model {model_name} not found. Falling back to {fallback}."
                )
                return ChatGoogleGenerativeAI(
                    model=fallback, temperature=temperature, **kwargs
                )
            raise
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
