import time
import json
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.i18n import get_prompts

def create_risky_debator(llm):
    def risky_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        risky_history = risk_debate_state.get("risky_history", "")

        current_safe_response = risk_debate_state.get("current_safe_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

        prompt = get_prompts("risk_mgmt", "aggressive_debator") \
            .replace("{max_tokens}", str(DEFAULT_CONFIG["max_tokens"])) \
            .replace("{trader_decision}", trader_decision) \
            .replace("{market_research_report}", market_research_report) \
            .replace("{sentiment_report}", sentiment_report) \
            .replace("{news_report}", news_report) \
            .replace("{fundamentals_report}", fundamentals_report) \
            .replace("{history}", history) \
            .replace("{current_safe_response}", current_safe_response) \
            .replace("{current_neutral_response}", current_neutral_response)

        response = llm.invoke(prompt)

        argument = f"Risky Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risky_history + "\n" + argument,
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Risky",
            "current_risky_response": argument,
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return risky_node
