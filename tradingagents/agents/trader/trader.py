import functools
import time
import json
from tradingagents.i18n import get_prompts

def create_trader(llm, memory):
    def trader_node(state, name):
        asset_name = state["asset_of_interest"]
        investment_plan = state["investment_plan"]
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        external_reports = state.get("external_reports", [])

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        context = {
            "role": "user",
            "content": get_prompts("trader", "user_message") \
                .replace("{asset_name}", asset_name) \
                .replace("{investment_plan}", investment_plan) \
                .replace("{external_reports}", "\n".join(external_reports))
        }

        messages = [
            {
                "role": "system",
                "content": get_prompts("trader", "system_message") \
                    .replace("{past_memory_str}", past_memory_str),
            },
            context,
        ]

        result = llm.invoke(messages)

        return {
            "messages": [result],
            "trader_investment_plan": result.content,
            "sender": name,
        }

    return functools.partial(trader_node, name="Trader")
