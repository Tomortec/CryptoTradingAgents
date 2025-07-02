from functools import reduce
import importlib
from tradingagents.default_config import DEFAULT_CONFIG

def get_value(dictionary: dict, *keys, default=None):
    """
    Get values from a dictionary using a list of keys.
    If a key is not found, it returns the default value.
    """
    try:
        return reduce((lambda d, key: d[key]), keys, dictionary)
    except (KeyError, TypeError):
        return default

def get_lang(*keys, default="") -> str | dict:
    lang_code = DEFAULT_CONFIG.get("language", "zh")
    try:
        lang_module = importlib.import_module(f"tradingagents.i18n.{lang_code}")
        if not keys:
            return lang_module.LANG
        return get_value(lang_module.LANG, *keys, default=default)
    except Exception:
        # fallback to zh
        from .interface.zh import LANG
        if not keys:
            return LANG
        return get_value(LANG, *keys, default=default) 
    
def get_prompts(*keys, default="") -> str:
    lang_code = DEFAULT_CONFIG.get("language", "zh")
    try:
        lang_module = importlib.import_module(f"tradingagents.i18n.{lang_code}")
        return get_value(lang_module.PROMPTS, *keys, default=default)
    except Exception:
        # fallback to zh
        from .prompts.zh import PROMPTS
        return get_value(PROMPTS, *keys, default=default)