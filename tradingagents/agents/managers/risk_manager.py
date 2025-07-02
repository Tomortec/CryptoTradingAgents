import time
import json
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.i18n import get_prompts

def create_risk_manager(llm, memory):
    def risk_manager_node(state) -> dict:

        asset_name = state["asset_of_interest"]

        history = state["risk_debate_state"]["history"]
        risk_debate_state = state["risk_debate_state"]
        market_research_report = state["market_report"]
        news_report = state["news_report"]
        fundamentals_report = state["news_report"]
        sentiment_report = state["sentiment_report"]
        investment_preferences = state.get("investment_preferences", "")
        external_reports = state.get("external_reports", [])
        trader_plan = state["investment_plan"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = get_prompts("managers", "risk_manager") \
            .replace("{max_tokens}", str(DEFAULT_CONFIG["max_tokens"])) \
            .replace("{trader_plan}", trader_plan) \
            .replace("{past_memory_str}", past_memory_str) \
            .replace("{history}", history) \
            .replace("{external_reports}", "\n".join(external_reports)) \
            + "\n\n" \
            + get_prompts("investment_preferences", "system_message") \
            .replace("{investment_preferences}", investment_preferences)
        
        response = llm.invoke(prompt)

        new_risk_debate_state = {
            "judge_decision": response.content,
            "history": risk_debate_state["history"],
            "risky_history": risk_debate_state["risky_history"],
            "safe_history": risk_debate_state["safe_history"],
            "neutral_history": risk_debate_state["neutral_history"],
            "latest_speaker": "Judge",
            "current_risky_response": risk_debate_state["current_risky_response"],
            "current_safe_response": risk_debate_state["current_safe_response"],
            "current_neutral_response": risk_debate_state["current_neutral_response"],
            "count": risk_debate_state["count"],
        }

        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": response.content,
        }

    return risk_manager_node
