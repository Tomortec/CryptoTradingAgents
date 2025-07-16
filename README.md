# Crypto Trading Agents

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-0.1.0--preview-yellow.svg)](./VERSION)
[![Docs](https://img.shields.io/badge/Docs-中文文档-green.svg)](./README-CN.md)
[![Original](https://img.shields.io/badge/Base%20On-TauricResearch/TradingAgents-orange.svg)](https://github.com/TauricResearch/TradingAgents)
[![Paper](https://img.shields.io/badge/Paper-arxiv%202412.20138-blue.svg)](https://arxiv.org/pdf/2412.20138)

[中文文档](./README-CN.md)

## 🙏 Acknowledgements
This project is based on [TradingAgents](https://github.com/TauricResearch/TradingAgents) by the [Tauric Research](https://github.com/TauricResearch) team, as well as the paper [arxiv.org/pdf/2412.20138](https://arxiv.org/pdf/2412.20138).
We extend our sincere thanks for their contributions!

In addition, the following authors and repositories also inspired this project:
| Author | Repository |
| --- | --- |
| [@delenzhang](https://github.com/delenzhang) | [TradingAgents](https://github.com/delenzhang/TradingAgents) |
| [@hsliuping](https://github.com/hsliuping)   | [TradingAgents-CN](https://github.com/hsliuping/TradingAgents-CN) |

## ✨ Key Features
💰 **Crypto-Focused**  
Built upon the TradingAgents framework, specifically adjusted for cryptocurrency assets.  
📈 **Integrated Technical Analysis**  
Pulls data from professional technical analysis platforms instead of relying solely on LLM interpretation, reducing unreliable qualitative fluff. [Supported Infomation Sources](#supported-information-sources)  
📰 **Targeted News Sources**  
Collects data from sources frequently used by crypto traders — reliable, relevant, and free! [Supported Infomation Sources](#supported-information-sources)  
❤️ **Tailored to Your Trading Style**  
You can define custom investment preferences—whether you're an aggressive trader or a long-term investor, your style and strategy will be reflected in the report. [Configure Investment Preferences](#4-optional-configure-investment-preferences)  
🚀 **Incorporate External Reports**  
You can provide external researches or opinions for consideration—more context leads to better insights. [Steps to Use](#steps-to-use)  
📄 **PDF or Markdown Report Generation**  
Analysis reports are generated in readable formats.  
📧 **Scheduled Email Delivery**  
Combine with OS-level task schedulers to automatically generate and email reports - get market updates like you're the head of a trading desk.  
🎥 **Real-Time Report Logging**  
Generated reports are written to log files under ./logs in real time. Even if the process is interrupted or encounters an error, the partial report remains available—ensuring your API usage is never wasted.  
⚙️ **Fully Customizable**  
Easily modify or add new data sources. A detailed guide is provided to help you quickly adapt the tool to your needs. [Customization](#customization)

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
#### 1. Configure LLM API Key
Create a `.env` file under the `./cli` directory using `.env.example` and fill in your LLM API key, such as:  
For Qwen: `DASHSCOPE_API_KEY=XXXXXX`  
For ChatGPT: `OPENAI_API_KEY=XXXXXX`  
> See [Supported LLMs and API Key Naming](#supported-llms)

#### 2. Configure Information Source API Keys
Also add the required API keys for data sources into the `./cli/.env` file
> See [Supported Information Sources](#supported-information-sources)

#### 3. Check and Modify Configuration
Edit [`./tradingagents/default_config.py`](./tradingagents/default_config.py) to change the language, LLM settings, and other default configurations.

#### 4. (Optional) Configure Investment Preferences
Create a file named `investment_preferences` in the `./cli` directory to define custom investment preferences.

#### 5. (Optional) Configure Email Sending
Set `send_report_to_email = True` in [`default_config.py`](./tradingagents/default_config.py),  
then copy `./mailsender/.env.example` to `.env` and fill in the email settings.

### Running the Program

You can use [**CLI Mode**](#cli-mode) or [**Script Mode**](#script-mode).  
CLI mode includes an interactive terminal interface; script mode is ideal for automation (e.g., hourly scheduled reports).

#### CLI Mode 
Execute the main program from terminal:
```sh
python -m cli.main
```

##### Steps to Use
1. **Enter Asset Symbol**, such as BTC or ETH
2. **Enter Analysis Date**
3. **Select Analyst Team** - `Market Analyst`, `Social Media Analyst`, `News Analyst` and `Fundamentals Analyst`
4. **Choose Research Depth**
5. **Import External Reports**: Type `y` and press Enter to open the default editor, where you can input external viewpoints for the model to consider. Save the file when done.
6. **Import Investment Preferences**: Use the saved file at `./cli/investment_preferences` or input them directly in the editor (optional).
7. **Select LLM Model**
8. **Generate Report**: After processing, the report will be saved under [`./tradingagents/reports`](./tradingagents/reports).

#### Script Mode
1. Edit `./cli/run.py` as needed (e.g., set ticker or date)
2. Run the script:
```sh
python -m cli.run
```

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
* [x] Add LLM search capabilities for richer information retrieval
* [x] Enable automatic report delivery
* [ ] Integrate with freqtrade for backtesting/simulated trading
* [ ] Provide more LLMs, such as DeepSeek (use Qwen's Embedding)
* [ ] Improve prompt templates using latest LLM research
* [ ] Provide a UI interface
* [ ] ~~Integrate other price forecasting tools~~ (You can implement your own with [Customize Data Sources](#customize-data-sources). For forecasting tools, see [CryptoMamba](https://github.com/MShahabSepehri/CryptoMamba), [Cryptopulse](https://github.com/aamitssharma07/SAL-Cryptopulse), etc.)

## ⚠️ Disclaimer
This project is for research and educational purposes only and does **not constitute investment advice**. Investing involves risk—make decisions cautiously.

<br/>

---
We welcome contributions! Including but not limited to **submitting issues, fixing bugs, adding features, improving documentation, and localization**.  
⭐️⭐️ If this project helps you, please consider giving us a star! ⭐️⭐️
