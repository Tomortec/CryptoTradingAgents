from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from datetime import datetime
import json
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.i18n import get_prompts

def create_market_analyst(llm, toolkit):

    def market_analyst_node(state):
        date_to_research = state["trade_date"]
        ticker = state["asset_of_interest"]
        asset_name = state["asset_of_interest"]
        investment_preferences = state.get("investment_preferences", "")

        tools = [
            toolkit.get_binance_data,
            toolkit.get_taapi_bulk_indicators
        ]

        system_message = (
            get_prompts("analysts", "market_analyst", "system_message")
                .replace("{max_tokens}", str(DEFAULT_CONFIG["max_tokens"]))
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    get_prompts("analysts", "template")
                ),
                (
                    "system",
                    get_prompts("user_preferences", "system_message")
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(investment_preferences=investment_preferences)
        prompt = prompt.partial(current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        prompt = prompt.partial(date_to_research=date_to_research)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content
       
        return {
            "messages": [result],
            "market_report": report,
        }

    return market_analyst_node
