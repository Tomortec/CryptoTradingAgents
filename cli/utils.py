import questionary
from typing import List, Optional, Tuple, Dict
from markdown_pdf import MarkdownPdf, Section

from cli.models import AnalystType
from tradingagents.i18n import get_lang

lang = get_lang()

ANALYST_ORDER = [
    ("Market Analyst", AnalystType.MARKET),
    ("Social Media Analyst", AnalystType.SOCIAL),
    ("News Analyst", AnalystType.NEWS),
    ("Fundamentals Analyst", AnalystType.FUNDAMENTALS),
]


def get_ticker() -> str:
    """Prompt the user to enter a ticker symbol."""
    ticker = questionary.text(
        get_lang("step1_prompt"),
        validate=lambda x: len(x.strip()) > 0 or get_lang("ticker_validate"),
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not ticker:
        exit(1)

    return ticker.strip().upper()


def get_analysis_date() -> str:
    """Prompt the user to enter a date in YYYY-MM-DD format."""
    import re
    from datetime import datetime

    def validate_date(date_str: str) -> bool:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    date = questionary.text(
        get_lang("step2_prompt"),
        validate=lambda x: validate_date(x.strip()) or get_lang("date_validate"),
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not date:
        exit(1)

    return date.strip()


def select_analysts() -> List[AnalystType]:
    """Select analysts using an interactive checkbox."""
    choices = questionary.checkbox(
        get_lang("step3_prompt"),
        choices=[
            questionary.Choice(lang.get(display.replace(" ", "_").lower(), display), value=value) for display, value in ANALYST_ORDER
        ],
        instruction=get_lang("analyst_instruction"),
        validate=lambda x: len(x) > 0 or get_lang("analyst_validate"),
        style=questionary.Style(
            [
                ("checkbox-selected", "fg:green"),
                ("selected", "fg:green noinherit"),
                ("highlighted", "noinherit"),
                ("pointer", "noinherit"),
            ]
        ),
    ).ask()

    if not choices:
        exit(1)

    return choices


def select_research_depth() -> int:
    """Select research depth using an interactive selection."""

    # Define research depth options with their corresponding values
    DEPTH_OPTIONS = [
        (get_lang("depth_shallow"), 1),
        (get_lang("depth_medium"), 3),
        (get_lang("depth_deep"), 5),
    ]

    choice = questionary.select(
        get_lang("step4_prompt"),
        choices=[
            questionary.Choice(display, value=value) for display, value in DEPTH_OPTIONS
        ],
        instruction=get_lang("depth_instruction"),
        style=questionary.Style(
            [
                ("selected", "fg:yellow noinherit"),
                ("highlighted", "fg:yellow noinherit"),
                ("pointer", "fg:yellow noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        exit(1)

    return choice


def select_shallow_thinking_agent(provider) -> str:
    """Select shallow thinking llm engine using an interactive selection."""

    # Define shallow thinking llm engine options with their corresponding model names
    SHALLOW_AGENT_OPTIONS = {
        "openai": [
            ("GPT-4o-mini - Fast and efficient for quick tasks", "gpt-4o-mini"),
            ("GPT-4.1-nano - Ultra-lightweight model for basic operations", "gpt-4.1-nano"),
            ("GPT-4.1-mini - Compact model with good performance", "gpt-4.1-mini"),
            ("GPT-4o - Standard model with solid capabilities", "gpt-4o"),
        ],
        "qwen": [
            ("Qwen-Turbo - Fast speed and low cost, suitable for simple tasks", "qwen-turbo-latest"),
            ("Qwen-Plus - Balanced combination of performance and speed, ideal for moderately complex tasks", "qwen-plus-latest"),
            ("Qwen-Max - For complex and multi-step tasks", "qwen-max-latest"),
            ("Qwen-Long - For long context tasks", "qwen-long")
        ],
        "anthropic": [
            ("Claude Haiku 3.5 - Fast inference and standard capabilities", "claude-3-5-haiku-latest"),
            ("Claude Sonnet 3.5 - Highly capable standard model", "claude-3-5-sonnet-latest"),
            ("Claude Sonnet 3.7 - Exceptional hybrid reasoning and agentic capabilities", "claude-3-7-sonnet-latest"),
            ("Claude Sonnet 4 - High performance and excellent reasoning", "claude-sonnet-4-0"),
        ],
        "google": [
            ("Gemini 2.0 Flash-Lite - Cost efficiency and low latency", "gemini-2.0-flash-lite"),
            ("Gemini 2.0 Flash - Next generation features, speed, and thinking", "gemini-2.0-flash"),
            ("Gemini 2.5 Flash - Adaptive thinking, cost efficiency", "gemini-2.5-flash-preview-05-20"),
        ],
        "openrouter": [
            ("Meta: Llama 4 Scout", "meta-llama/llama-4-scout:free"),
            ("Meta: Llama 3.3 8B Instruct - A lightweight and ultra-fast variant of Llama 3.3 70B", "meta-llama/llama-3.3-8b-instruct:free"),
            ("google/gemini-2.0-flash-exp:free - Gemini Flash 2.0 offers a significantly faster time to first token", "google/gemini-2.0-flash-exp:free"),
        ],
        "ollama": [
            ("llama3.2 local", "llama3.2"),
        ]
    }

    choice = questionary.select(
        "Select Your [Quick-Thinking LLM Engine]:",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in SHALLOW_AGENT_OPTIONS[provider.lower()]
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        exit(1)

    return choice


def select_deep_thinking_agent(provider) -> str:
    """Select deep thinking llm engine using an interactive selection."""

    # Define deep thinking llm engine options with their corresponding model names
    DEEP_AGENT_OPTIONS = {
        "openai": [
            ("GPT-4.1-nano - Ultra-lightweight model for basic operations", "gpt-4.1-nano"),
            ("GPT-4.1-mini - Compact model with good performance", "gpt-4.1-mini"),
            ("GPT-4o - Standard model with solid capabilities", "gpt-4o"),
            ("o4-mini - Specialized reasoning model (compact)", "o4-mini"),
            ("o3-mini - Advanced reasoning model (lightweight)", "o3-mini"),
            ("o3 - Full advanced reasoning model", "o3"),
            ("o1 - Premier reasoning and problem-solving model", "o1"),
        ],
        "qwen": [
            ("QwQ - Reasoning model. Have reached the level of DeepSeek-R1", "qwq-plus"),
            ("Qwen-Turbo - Fast speed and low cost, suitable for simple tasks", "qwen-turbo-latest"),
            ("Qwen-Plus - Balanced combination of performance and speed, ideal for moderately complex tasks", "qwen-plus-latest"),
            ("Qwen-Max - For complex and multi-step tasks", "qwen-max-latest"),
            ("Qwen-Long - For long context tasks", "qwen-long"),
        ],
        "anthropic": [
            ("Claude Haiku 3.5 - Fast inference and standard capabilities", "claude-3-5-haiku-latest"),
            ("Claude Sonnet 3.5 - Highly capable standard model", "claude-3-5-sonnet-latest"),
            ("Claude Sonnet 3.7 - Exceptional hybrid reasoning and agentic capabilities", "claude-3-7-sonnet-latest"),
            ("Claude Sonnet 4 - High performance and excellent reasoning", "claude-sonnet-4-0"),
            ("Claude Opus 4 - Most powerful Anthropic model", "	claude-opus-4-0"),
        ],
        "google": [
            ("Gemini 2.0 Flash-Lite - Cost efficiency and low latency", "gemini-2.0-flash-lite"),
            ("Gemini 2.0 Flash - Next generation features, speed, and thinking", "gemini-2.0-flash"),
            ("Gemini 2.5 Flash - Adaptive thinking, cost efficiency", "gemini-2.5-flash-preview-05-20"),
            ("Gemini 2.5 Pro", "gemini-2.5-pro-preview-06-05"),
        ],
        "openrouter": [
            ("DeepSeek V3 - a 685B-parameter, mixture-of-experts model", "deepseek/deepseek-chat-v3-0324:free"),
            ("Deepseek - latest iteration of the flagship chat model family from the DeepSeek team.", "deepseek/deepseek-chat-v3-0324:free"),
        ],
        "ollama": [
            ("qwen3", "qwen3"),
        ]
    }
    
    choice = questionary.select(
        "Select Your [Deep-Thinking LLM Engine]:",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in DEEP_AGENT_OPTIONS[provider.lower()]
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        exit(1)

    return choice

def select_llm_provider() -> tuple[str, str]:
    """Select the OpenAI api url using interactive selection."""
    # Define OpenAI api options with their corresponding endpoints
    BASE_URLS = [
        ("OpenAI", "https://api.openai.com/v1"),
        ("Qwen", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        ("Anthropic", "https://api.anthropic.com/"),
        ("Google", "https://generativelanguage.googleapis.com/v1"),
        ("Openrouter", "https://openrouter.ai/api/v1"),
        ("Ollama", "http://localhost:11434/v1"),        
    ]
    
    choice = questionary.select(
        "Select your LLM Provider:",
        choices=[
            questionary.Choice(display, value=(display, value))
            for display, value in BASE_URLS
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()
    
    if choice is None:
        exit(1)
    
    display_name, url = choice
    print(f"You selected: {display_name}\tURL: {url}")
    
    return display_name, url

def extract_reports_from_final_state(final_state):
    analyst_reports = []
    if final_state.get("market_report"):
        analyst_reports.append(("Market Analyst", final_state["market_report"]))
    if final_state.get("sentiment_report"):
        analyst_reports.append(("Sentiment Analyst", final_state["sentiment_report"]))
    if final_state.get("news_report"):
        analyst_reports.append(("News Analyst", final_state["news_report"]))
    if final_state.get("fundamentals_report"):
        analyst_reports.append(("Fundamentals Analyst", final_state["fundamentals_report"]))
    if final_state.get("investment_debate_state"):
        debate_state = final_state["investment_debate_state"]
        if debate_state.get("bull_history"):
            analyst_reports.append(("Investment Debate - Bull", debate_state["bull_history"]))
        if debate_state.get("bear_history"):
            analyst_reports.append(("Investment Debate - Bear", debate_state["bear_history"]))
        if debate_state.get("judge_decision"):
            analyst_reports.append(("Investment Debate - Judge Decision", debate_state["judge_decision"]))
    if final_state.get("trader_investment_plan"):
        analyst_reports.append(("Trader Investment Plan", final_state["trader_investment_plan"]))
    if final_state.get("risk_debate_state"):
        risk_state = final_state["risk_debate_state"]
        if risk_state.get("risky_history"):
            analyst_reports.append(("Risk Debate - Risky", risk_state["risky_history"]))
        if risk_state.get("safe_history"):
            analyst_reports.append(("Risk Debate - Safe", risk_state["safe_history"]))
        if risk_state.get("neutral_history"):
            analyst_reports.append(("Risk Debate - Neutral", risk_state["neutral_history"]))
        if risk_state.get("judge_decision"):
            analyst_reports.append(("Risk Debate - Judge Decision", risk_state["judge_decision"]))
    return {report_name: report_content for report_name, report_content in analyst_reports if report_content}

def save_reports(ticker: str, reports: Dict[str, str], output_dir: str, file_type = "pdf", filename = "", decision: str = "") -> None:
    """
        Save the generated reports to the specified output directory.
        Args:
            ticker (str): The ticker symbol for which the reports are generated.
            reports (Dict[str, str]): A dictionary where keys are report names and values are report content.
            output_dir (str): The directory where the reports will be saved.
            file_type (str): The type of file to save the reports as, either "pdf" or "md". Defaults to "pdf".
            filename (str): Optional filename to save the reports as a single file. If empty, the filename will be formatted as `{ticker}_reports_{time}`.
            decision (str): "Buy", "Sell", or "Hold" decision to include in the report file name.
    """
    import os
    from datetime import datetime

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_type = "md" if file_type.lower() == "md" else "pdf"

    if filename:
        file_path = os.path.join(output_dir, filename)
    else:
        time_str = datetime.now().strftime("%Y%m%d_%H%M")
        file_path = os.path.join(output_dir, f"{ticker}_reports{("_"+decision if decision else "")}_{time_str}.{file_type}")

    header = f"# Reports for {ticker}\n\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

    if file_type == "md":
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(header)
            for report_name, report_content in reports.items():
                file.write(f"## {report_name}\n\n")
                file.write(report_content + "\n\n")
            if decision:
                file.write(f"## Final Decision: {decision.capitalize()}\n\n")
    else:
        pdf = MarkdownPdf(toc_level=7)
        decision_bgcolor = "#347433" if decision.lower() == "buy" else ("#B22222" if decision.lower() == "sell" else "#F1A71C")
        decision_html = f"<div style='background-color: {decision_bgcolor}; padding: 10px; color: white; text-align: center; font-weight: bold; margin-bottom: 20px;'>Decision: {decision.capitalize()}</div>\n\n" if decision else ""
        header_html = f"<h1 style='font-size: 72px; margin-bottom: 420px;'>Reports for {ticker}</h1>\n\n" + \
            decision_html + \
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        pdf.add_section(Section(header_html))
        for report_name, report_content in reports.items():
            pdf.add_section(Section(f"## {report_name}\n\n{report_content}", toc=False))
        pdf.meta["title"] = f"Reports for {ticker}"
        pdf.meta["author"] = "Crypto Trading Agents"
        pdf.save(file_path)