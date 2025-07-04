from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from datetime import datetime
import json
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.i18n import get_prompts

def create_news_analyst(llm, toolkit):
    def news_analyst_node(state):
        date_to_research = state["trade_date"]
        ticker = state["asset_of_interest"]

        tools = [
            toolkit.get_binance_ohlcv,
            # toolkit.get_global_news_openai, 
            # toolkit.get_google_news,
            # toolkit.get_reddit_news,
            toolkit.get_blockbeats_news,
            toolkit.get_coindesk_news,
            toolkit.get_coinstats_news,
            toolkit.get_fear_and_greed_index
        ]

        system_message = (
            get_prompts("analysts", "news_analyst", "system_message")
                .replace("{max_tokens}", str(DEFAULT_CONFIG["max_tokens"]))
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    get_prompts("analysts", "template")
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
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
            "news_report": report,
        }

    return news_analyst_node
