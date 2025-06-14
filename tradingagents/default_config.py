import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "data_dir": "/Users/yluo/Documents/Code/ScAI/FR1-data",
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings
    "deep_think_llm": "o4-mini",
    "quick_think_llm": "gpt-4o-mini",
    # New LLM providers
    "deepseek_api_key": os.getenv("DEEPSEEK_API_KEY", ""),
    "google_api_key": os.getenv("GOOGLE_API_KEY", ""),
    "deepseek_model": "deepseek-chat",
    "gemini_model": "gemini-2.5-flash-preview-05-20",
    "llm_providers": {
        "deep_think": "deepseek",
        "quick_think": "deepseek"
    },
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Tool settings
    "online_tools": True,
}
