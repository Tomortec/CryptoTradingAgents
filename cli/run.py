from dotenv import load_dotenv
load_dotenv()

import datetime
from time import sleep
from loguru import logger

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from .models import AnalystType
from .utils import extract_reports_from_final_state, save_reports
from mailsender import send, send_email_with_body

def get_investment_preferences():
    def drop_sharp_starting_lines(text: str):
        """Remove sharp starting lines from the text."""
        lines = text.splitlines()
        return "\n".join(line for line in lines if not line.strip().startswith("#"))

    try:
        with open("./cli/investment_preferences", "r") as f:
            preferences = f.read()
            return drop_sharp_starting_lines(preferences) if preferences else ""
    except FileNotFoundError:
        logger.warning("Investment preferences file not found. Using default preferences.")
        return ""

def run_analysis(
    ticker: str, analysis_date: str, 
    analysts: list[AnalystType],
    investment_preferences: str = "",
    external_reports: list[str] = [] 
):
    logger.add("logs/reports.log", rotation="1 day", retention="7 days", level="SUCCESS")
    graph = TradingAgentsGraph(
        [analyst.value for analyst in analysts], 
        config=DEFAULT_CONFIG
    )

    # Initialize state and get graph args
    init_agent_state = graph.propagator.create_initial_state(
        asset_name=ticker,
        trade_date=analysis_date,
        investment_preferences=investment_preferences,
        external_reports=external_reports
    )
    args = graph.propagator.get_graph_args()

    # Stream the analysis
    trace = []
    completion_status = {}
    for chunk in graph.graph.stream(init_agent_state, **args):
        if len(chunk["messages"]) > 0:
            
            last_message = chunk["messages"][-1]
            if hasattr(last_message, "tool_calls"):
                for tool_call in last_message.tool_calls:
                    # Handle both dictionary and object tool calls
                    if isinstance(tool_call, dict):
                        logger.info(f"Tool call: {tool_call["name"]} with args: {tool_call["args"]}")
                    else:
                        logger.info(f"Tool call: {tool_call.name} with args: {tool_call.args}")
                        
            if "market_report" in chunk and chunk["market_report"] and completion_status.get("market_report", False) is False:
                logger.info(f"--- Market Analysis Completed ---")
                logger.success(f"Market Report: {chunk["market_report"]}")
                completion_status["market_report"] = True
                
            if "sentiment_report" in chunk and chunk["sentiment_report"] and completion_status.get("sentiment_report", False) is False:
                logger.info(f"--- Sentiment Analysis Completed ---")
                logger.success(f"Sentiment Report: {chunk["sentiment_report"]}")
                completion_status["sentiment_report"] = True
                
            if "news_report" in chunk and chunk["news_report"] and completion_status.get("news_report", False) is False:
                logger.info(f"--- News Analysis Completed ---")
                logger.success(f"News Report: {chunk["news_report"]}")
                completion_status["news_report"] = True
                
            if "fundamentals_report" in chunk and chunk["fundamentals_report"] and completion_status.get("fundamentals_report", False) is False:
                logger.info(f"--- Fundamentals Analysis Completed ---")
                logger.success(f"Fundamentals Report: {chunk["fundamentals_report"]}")
                completion_status["fundamentals_report"] = True
                
            if "investment_debate_state" in chunk and chunk["investment_debate_state"] and completion_status.get("investment_debate_state", False) is False:
                debate_state = chunk["investment_debate_state"]
                if "bull_history" in debate_state and debate_state["bull_history"] and completion_status.get("bull_history", False) is False:
                    logger.info("--- Research Team Debate (In Progress) ---")
                    logger.success(f"Bullish History: {debate_state["bull_history"]}")
                    completion_status["bull_history"] = True
                if "bear_history" in debate_state and debate_state["bear_history"] and completion_status.get("bear_history", False) is False:
                    logger.info("--- Research Team Debate (In Progress) ---")
                    logger.success(f"Bearish History: {debate_state["bear_history"]}")
                    completion_status["bear_history"] = True
                    
                if "judge_decision" in debate_state and debate_state["judge_decision"]:
                    logger.info(f"--- Research Team Debate Completed ---")
                    logger.success(f"Investment Judge Decision: {debate_state["judge_decision"]}")
                    completion_status["investment_debate_state"] = True
                    
            if "trader_investment_plan" in chunk and chunk["trader_investment_plan"] and completion_status.get("trader_investment_plan", False) is False:
                logger.info(f"--- Trader Investment Planning Completed ---")
                logger.success(f"Trader Investment Plan: {chunk["trader_investment_plan"]}")
                completion_status["trader_investment_plan"] = True
                
            if "risk_debate_state" in chunk and chunk["risk_debate_state"] and completion_status.get("risk_debate_state", False) is False:
                risk_state = chunk["risk_debate_state"]
                if "current_risky_response" in risk_state and risk_state["current_risky_response"] and completion_status.get("current_risky_response", False) is False:
                    logger.info(f"--- Risk Discussion - Risky (In Progress) ---")
                    logger.success(f"Current Risky Response: {risk_state["current_risky_response"]}")
                    completion_status["current_risky_response"] = True
                if "current_safe_response" in risk_state and risk_state["current_safe_response"] and completion_status.get("current_safe_response", False) is False:
                    logger.info(f"--- Risk Discussion - Safe (In Progress) ---")
                    logger.success(f"Current Safe Response: {risk_state["current_safe_response"]}")
                    completion_status["current_safe_response"] = True
                if "current_neutral_response" in risk_state and risk_state["current_neutral_response"] and completion_status.get("current_neutral_response", False) is False:
                    logger.info(f"--- Risk Discussion - Neutral (In Progress) ---")
                    logger.success(f"Current Neutral Response: {risk_state["current_neutral_response"]}")
                    completion_status["current_neutral_response"] = True
                    
                if "judge_decision" in risk_state and risk_state["judge_decision"] and completion_status.get("risk_judge_decision", False) is False:
                    logger.info(f"--- Risk Discussion Completed ---")
                    logger.success(f"Risk Judge Decision: {risk_state["judge_decision"]}")
                    logger.info("Analysis completed successfully.")
                    completion_status["risk_judge_decision"] = True
            
            trace.append(chunk)

    # Get final state and decision
    final_state = trace[-1]
    decision = graph.process_signal(final_state["final_trade_decision"]).capitalize()
    decision_color = "green" if decision == "Buy" else "red" if decision == "Sell" else "yellow"
    logger.level("FINAL", no=38, color=decision_color)
    logger.log("FINAL", f"Final Decision: {decision}")

    if DEFAULT_CONFIG["save_report"]:
        logger.info("Saving reports...")
        reports = extract_reports_from_final_state(final_state)
        save_reports(ticker, reports, DEFAULT_CONFIG["report_dir"], DEFAULT_CONFIG["report_type"], decision=decision)
        logger.info(f"Report saved to {DEFAULT_CONFIG['report_dir']}")

if __name__ == "__main__":
    try:
        run_analysis(
            ticker="BTC",
            analysis_date=datetime.date.today().strftime("%Y-%m-%d"),
            analysts=[
                AnalystType.MARKET,
                AnalystType.SOCIAL,
                AnalystType.NEWS
            ],
            investment_preferences=get_investment_preferences(),
            external_reports=[]
        )
        if DEFAULT_CONFIG["send_report_to_email"]:
            sleep(1)  # Allow time for any background tasks to complete
            logger.info("Sending email report...")
            send()
            logger.info("Email report sent successfully.")
            logger.info("Execution completed successfully. Now exiting.")
    except Exception as e:
        logger.error(f"An error occurred during analysis: {e}")
        send_email_with_body(f"An error occurred during the analysis: {e}")