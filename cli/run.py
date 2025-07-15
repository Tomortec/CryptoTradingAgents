from dotenv import load_dotenv
load_dotenv()

import datetime
from time import sleep
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
        print("Investment preferences file not found. Using default preferences.")
        return ""

def run_analysis(
    ticker: str, analysis_date: str, 
    analysts: list[AnalystType],
    investment_preferences: str = "",
    external_reports: list[str] = [] 
):
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
    for chunk in graph.graph.stream(init_agent_state, **args):
        trace.append(chunk)

    # Get final state and decision
    final_state = trace[-1]
    decision = graph.process_signal(final_state["final_trade_decision"])

    if DEFAULT_CONFIG["save_report"]:
        reports = extract_reports_from_final_state(final_state)
        save_reports(ticker, reports, DEFAULT_CONFIG["report_dir"], DEFAULT_CONFIG["report_type"], decision=decision)

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
        sleep(1)  # Allow time for any background tasks to complete
        send()
    except Exception as e:
        print(f"An error occurred during analysis: {e}")
        send_email_with_body(f"An error occurred during the analysis: {e}")