import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "data_dir": "/Users/yluo/Documents/Code/ScAI/FR1-data",
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # Output settings
    "save_report": True,
    "report_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")), "reports"
    ),
    # LLM settings
    "llm_provider": "qwen",
    "deep_think_llm": "qwen-plus",
    "quick_think_llm": "qwen-turbo",
    "backend_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "api_key_env_name": "DASHSCOPE_API_KEY",
    "max_tokens": 4096,  # Maximum tokens for LLM responses
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 200,
    # Language settings
    "language": "zh",  # 支持 'zh' 或 'en'
}
