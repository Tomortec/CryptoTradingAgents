# Dataflows

### To add a new data source
1. create a file with filename `[sth]_utils.py` and fetch data in it
2. go to [interface.py](./interface.py) and wrap your utility in a function returning a `str`
3. go to [\_\_init\_\_.py](./__init__.py) and expose your function in `interface.py`
4. go to [agent_utils.py](../agents/utils/agent_utils.py) and wrap your function in class `Toolkit` with the following template:
    ``` py
    @staticmethod
    @tool
    def get_sth(params: Annotated[type, "comments"]):
        """docs"""
        return interface.your_func(params)
    ```
5. modify `_create_tool_nodes` in [trading_graph.py](../graph/trading_graph.py) and `news_analyst_node` in each analyst creation file in `tradingagents/agents/analysts/[sth]_analyst.py`
6. (OPTIONAL) modify prompts to tell models when to use the utility