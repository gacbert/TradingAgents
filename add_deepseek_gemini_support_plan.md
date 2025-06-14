# Implementation Plan: Adding DeepSeek and Gemini Support

## Overview
This document outlines the steps to add support for DeepSeek and Gemini LLM providers to the TradingAgents project.

## Configuration Updates
### File: `tradingagents/default_config.py`
```python
# Add to existing DEFAULT_CONFIG
"deepseek_api_key": os.getenv("DEEPSEEK_API_KEY", ""),
"google_api_key": os.getenv("GOOGLE_API_KEY", ""),
"deepseek_model": "deepseek-chat",
"gemini_model": "gemini-1.5-flash-preview",
"llm_providers": {
    "deep_think": "deepseek",
    "quick_think": "gemini"
}
```

## Model Initialization
### File: `tradingagents/agents/utils/agent_utils.py`
```python
# Add new imports
from langchain_community.chat_models import ChatDeepSeek
from langchain_google_genai import ChatGoogleGenerativeAI

# Add to Toolkit class
def get_llm(self, llm_type="deep_think"):
    provider = self.config["llm_providers"].get(llm_type, "openai")
    
    if provider == "deepseek":
        return ChatDeepSeek(
            model=self.config["deepseek_model"],
            api_key=self.config["deepseek_api_key"]
        )
    elif provider == "gemini":
        return ChatGoogleGenerativeAI(
            model=self.config["gemini_model"],
            google_api_key=self.config["google_api_key"],
            temperature=0.7
        )
    else:  # Default to OpenAI
        return ChatOpenAI(model=self.config["quick_think_llm"])
```

## Agent Integration
All agent creation functions need to use `toolkit.get_llm()` instead of direct LLM instances.

### Example: `main.py` (or equivalent)
```python
# Before
social_media_analyst = create_social_media_analyst(ChatOpenAI(), toolkit)

# After
social_media_analyst = create_social_media_analyst(
    toolkit.get_llm("quick_think"), 
    toolkit
)
```

## Documentation Updates
### File: `README.md`
Add the following sections:

```markdown
## New LLM Providers

### Installation
```bash
pip install langchain-google-genai
pip install langchain-deepseek
```

### Environment Variables
```bash
export DEEPSEEK_API_KEY=your_api_key_here
export GOOGLE_API_KEY=your_api_key_here
```

### Configuration
- `deep_think` provider: DeepSeek (deepseek-chat)
- `quick_think` provider: Gemini (gemini-1.5-flash-preview)
```

### File: `.gitignore`
Add:
```
# API keys
*.env
*.key
```

## Implementation Notes
1. The `get_llm()` method handles provider selection based on configuration
2. Gemini uses the flash-preview model for quick responses
3. Fallback to OpenAI if providers are not configured