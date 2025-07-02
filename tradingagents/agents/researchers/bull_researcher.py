from langchain_core.messages import AIMessage
import time
import json
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.i18n import get_prompts

def create_bull_researcher(llm, memory):
    def bull_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")

        current_response = investment_debate_state.get("current_response", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        investment_preferences = state.get("investment_preferences", "")

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = get_prompts("researchers", "bull_researcher") \
            .replace("{max_tokens}", str(DEFAULT_CONFIG["max_tokens"])) \
            .replace("{market_research_report}", market_research_report) \
            .replace("{sentiment_report}", sentiment_report) \
            .replace("{news_report}", news_report) \
            .replace("{fundamentals_report}", fundamentals_report) \
            .replace("{history}", history) \
            .replace("{current_response}", current_response) \
            .replace("{past_memory_str}", past_memory_str) \
            + "\n\n" \
            + get_prompts("investment_preferences", "system_message") \
            .replace("{investment_preferences}", investment_preferences)
        
        response = llm.invoke(prompt)

        argument = f"Bull Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bull_node
