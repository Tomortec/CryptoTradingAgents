from langchain_core.messages import AIMessage
import time
import json
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.i18n import get_prompts

def create_safe_debator(llm):
    def safe_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        safe_history = risk_debate_state.get("safe_history", "")

        current_risky_response = risk_debate_state.get("current_risky_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]
        investment_preferences = state.get("investment_preferences", "")

        prompt = get_prompts("risk_mgmt", "conservative_debator") \
            .replace("{max_tokens}", str(DEFAULT_CONFIG["max_tokens"])) \
            .replace("{trader_decision}", trader_decision) \
            .replace("{market_research_report}", market_research_report) \
            .replace("{sentiment_report}", sentiment_report) \
            .replace("{news_report}", news_report) \
            .replace("{fundamentals_report}", fundamentals_report) \
            .replace("{history}", history) \
            .replace("{current_risky_response}", current_risky_response) \
            .replace("{current_neutral_response}", current_neutral_response) \
            + "\n\n" \
            + get_prompts("investment_preferences", "system_message") \
            .replace("{investment_preferences}", investment_preferences)
        
        response = llm.invoke(prompt)

        argument = f"Safe Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": safe_history + "\n" + argument,
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Safe",
            "current_risky_response": risk_debate_state.get(
                "current_risky_response", ""
            ),
            "current_safe_response": argument,
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return safe_node
