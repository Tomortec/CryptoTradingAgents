# Crypto Trading Agents

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-0.1.0--preview-yellow.svg)](./VERSION)
[![Docs](https://img.shields.io/badge/Docs-中文文档-green.svg)](./README-CN.md)
[![Original](https://img.shields.io/badge/Base%20On-TauricResearch/TradingAgents-orange.svg)](https://github.com/TauricResearch/TradingAgents)
[![Paper](https://img.shields.io/badge/Paper-arxiv%202412.20138-blue.svg)](https://arxiv.org/pdf/2412.20138)

[中文文档](./README-CN.md)

## 🛠️ Usage Guide
### Installation
Clone the repository:
```sh
git clone https://github.com/Tomortec/CryptoTradingAgents.git
cd TradingAgents
```

Create a virtual environment:
```sh
conda create -n tradingagents python=3.13
conda activate tradingagents
```

Install dependencies:
```sh
pip install -r requirements.txt
```

### Configuration
#### Configure LLM API Key
Create a `.env` file under the `./cli` directory and fill in your LLM API key, such as:  
For Qwen: `DASHSCOPE_API_KEY=XXXXXX`  
For ChatGPT: `OPENAI_API_KEY=XXXXXX`  
> See [Supported LLMs and API Key Naming](#supported-llms)

#### Configure Information Source API Keys
Also add the required API keys for data sources into the `./cli/.env` file
> See [Supported Information Sources](#supported-information-sources)

#### Check and Modify Configuration
Edit [`./tradingagents/default_config.py`](./tradingagents/default_config.py) to change the language, LLM settings, and other default configurations.

#### (Optional) Configure Investment Preferences
Create a file named `investment_preferences` in the `./cli` directory to define custom investment preferences.

#### Run the Program
Execute the main program from terminal:
```sh
python -m cli.main
```

### Steps to Use
1. **Enter Asset Symbol**, such as BTC or ETH
2. **Enter Analysis Date**, consistent with the source project
3. **Select Analyst Team**, consistent with the source project
4. **Choose Research Depth**, consistent with the source project
5. **Import External Reports**: Type `y` and press Enter to open the default editor, where you can input external viewpoints for the model to consider. Save the file when done.
6. **Import Investment Preferences**: Use the saved file at `./cli/investment_preferences` or input them directly in the editor (optional).
7. **Select LLM Model**, consistent with the source project
8. **Generate Report**: After processing, the report will be saved under [`./tradingagents/reports`](./tradingagents/reports).

### Supported LLMs
| Name                | API Variable        | Tested |
| ------------------- | ------------------- | ------ |
| Qwen (by Alibaba)   | `DASHSCOPE_API_KEY` | ✅      |
| ChatGPT (by OpenAI) | `OPENAI_API_KEY`    | ✅      |

### Supported Information Sources
|Source|Name|API Variable|Data Type|Registration|
|---|---|---|---| ---|
| [Alternative.me](https://alternative.me/crypto/fear-and-greed-index/)|Fear & Greed Index|None needed| Sentiment| N/A|
| [Binance](https://developers.binance.com/docs/zh-CN/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data) | K-line, market depth, 24h price change, long/short ratio|None needed| Market| N/A|
| [Blockbeats](https://github.com/BlockBeatsOfficial/RESTful-API)| Blockbeats News| None needed| News| N/A|
| [CoinDesk](https://developers.coindesk.com/documentation/data-api/news_v1_article_list)| CoinDesk News| `COINDESK_API_KEY`| News| [API Key Registration](https://developers.coindesk.com/settings/api-keys) |
| [CoinStats](https://docs.api.coinstats.app/reference/get-news)| CoinStats News| `COINSTATS_API_KEY`| News|[API Registration](https://openapi.coinstats.app)|
| [Reddit](https://praw.readthedocs.io/en/stable/)| Reddit Posts| `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USERNAME`, `REDDIT_PASSWORD`, `REDDIT_USER_AGENT` | Sentiment & News   | [Register App](https://old.reddit.com/prefs/apps/)|
| [taapi.io](https://taapi.io/indicators/)| Technical indicators like EMA, MACD, RSI, Supertrend, Bollinger Bands, Three White Soldiers, etc. | `TAAPI_API_KEY`| Technical Analysis | [My Account](https://taapi.io/my-account/) |

### Customization
#### Customize Prompts
Edit files under [`./tradingagents/i18n/prompts`](./tradingagents/i18n/prompts)
#### Customize Data Sources
Refer to [`./tradingagents/dataflows/README.md`](./tradingagents/dataflows/README.md)  
  
## 🔄 Planned Updates
* [ ] Add LLM search capabilities for richer information retrieval
* [ ] Provide more LLMs, such as DeepSeek (use Qwen's Embedding)
* [ ] Enable automatic report delivery
* [ ] Improve prompt templates using latest LLM research
* [ ] Integrate additional price prediction tools
* [ ] Provide a UI interface

## ⚠️ Disclaimer
This project is for research and educational purposes only and does **not constitute investment advice**. Investing involves risk—make decisions cautiously.

<br/>

---
We welcome contributions! Including but not limited to **submitting issues, fixing bugs, adding features, improving documentation, and localization**.  
⭐️⭐️ If this project helps you, please consider giving us a star! ⭐️⭐️
