# Crypto Trading Agents

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-0.1.0--preview-yellow.svg)](./VERSION)
[![Docs](https://img.shields.io/badge/Docs-Documentation-green.svg)](./README.md)
[![Original](https://img.shields.io/badge/Base%20On-TauricResearch/TradingAgents-orange.svg)](https://github.com/TauricResearch/TradingAgents)
[![Paper](https://img.shields.io/badge/Paper-arxiv%202412.20138-blue.svg)](https://arxiv.org/pdf/2412.20138)

## 感谢
本项目基于[Tauric Research](https://github.com/TauricResearch)团队的[TradingAgents](https://github.com/TauricResearch/TradingAgents)，以及[arxiv.org/pdf/2412.20138](https://arxiv.org/pdf/2412.20138)。在此表示诚挚的感谢！

此外，以下作者与仓库也为本仓库提供了思路：
|作者|仓库|
|---|---|
|[@delenzhang](https://github.com/delenzhang)|[TradingAgents](https://github.com/delenzhang/TradingAgents)|
|[@hsliuping](https://github.com/hsliuping)|[TradingAgents-CN](https://github.com/hsliuping/TradingAgents-CN)|

## 示例报告
[BTC-2025-07-01](./EXAMPLE_REPORT.md)

## 使用教程
### 安装
克隆仓库：
```sh
git clone https://github.com/Tomortec/CryptoTradingAgents.git
cd TradingAgents
```
创建虚拟环境：
```sh
conda create -n tradingagents python=3.13
conda activate tradingagents
```
安装依赖：
```sh
pip install -r requirements.txt
```

### 配置
#### 配置大模型 API_KEY
在`./cli`目录下创建`.env`文件，并填入大模型 API_KEY，例如：千问`DASHSCOPE_API_KEY=XXXXXX`、ChatGPT`OPENAI_API_KEY=XXXXXX`
> 查看[支持的大模型列表及API_KEY命名](#支持的大模型)
#### 配置信息源 API_KEY
在`./cli/.env`文件内填入信息源 API_KEY
> 查看[支持的信息源列表及API_KEY 命名](#支持的信息源列表)
#### 检查并修改配置
在[`./tradingagents/default_config.py`](./tradingagents/default_config.py)中修改语言、大模型配置
#### （可选）配置投资偏好
在`./cli`目录下创建`investment_preferences`文件，并填入投资偏好
#### 运行程序
在终端运行程序：
```sh
python -m cli.main
```

### 运行步骤
1. **输入资产代码**，例如 BTC、ETH  
2. **输入分析日期**，同源项目
3. **选择分析团队**，同源项目
4. **选择研究深度**，同源项目
5. **导入外部报告**，输入y并回车将打开默认编辑器，在其中可输入外部观点供大模型参考。输入完成后需保存
6. **导入投资偏好**，可使用`./cli/investment_preferences`文件中保存的投资偏好，也可在编辑器中输入（可留空）
7. **选择大模型**，同源项目
8. **获取分析报告**，等待分析完毕后，可在[`./tradingagents/reports`](./tradingagents/reports)目录下查看报告。报告示例：[BTC分析](./EXAMPLE_REPORT.md)

### 支持的大模型
|名称|API命名|是否测试可用|
|---|---|---|
|阿里通义千问Qwen|DASHSCOPE_API_KEY|✅|
|ChatGPT|OPENAI_API_KEY|✅|

### 支持的信息源列表
|来源|名称|API命名|信息类型|API 注册地址|
|---|---|---|---|---|
|[Alternative.me](https://alternative.me/crypto/fear-and-greed-index/)|恐惧贪婪指数|无需 API_KEY|情绪|无|
|[Binance](https://developers.binance.com/docs/zh-CN/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data)|K线数据、交易深度、24 小时价格变动、多空比等|无需 API_KEY|市场|无|
|[Blockbeats](https://github.com/BlockBeatsOfficial/RESTful-API)|Blockbeats 重要资讯|无需 API_KEY|新闻|无|
|[CoinDesk](https://developers.coindesk.com/documentation/data-api/news_v1_article_list)|CoinDesk 新闻|COINDESK_API_KEY|新闻|[https://developers.coindesk.com/settings/api-keys](https://developers.coindesk.com/settings/api-keys)|
|[CoinStats](https://docs.api.coinstats.app/reference/get-news)|CoinStats 新闻|COINSTATS_API_KEY|新闻|[https://openapi.coinstats.app](https://openapi.coinstats.app/)
|[Reddit](https://praw.readthedocs.io/en/stable/)|Reddit 帖子|REDDIT_CLIENT_ID、REDDIT_CLIENT_SECRET、REDDIT_USERNAME、REDDIT_PASSWORD、REDDIT_USER_AGENT|情绪与新闻|[https://old.reddit.com/prefs/apps](https://old.reddit.com/prefs/apps/)|
|[taapi.io](https://taapi.io/indicators/)|EMA、MACD、RSI、Supertrend、布林带、红三兵等|TAAPI_API_KEY|技术分析|[https://taapi.io/my-account](https://taapi.io/my-account/)|

### 自定义
#### 自定义提示词
修改[`./tradingagents/i18n/prompts`](./tradingagents/i18n/prompts)下的文件即可
#### 自定义信息源
请阅读[`./tradingagents/dataflows/README.md`](./tradingagents/dataflows/README.md)

## 后续可能的更新
- [ ] 开启大模型搜索功能以获取更丰富的信息
- [ ] 提供更多大模型，例如 DeepSeek（使用千问的Embedding模型）
- [ ] 自动发送报告
- [ ] 结合最新 LLM 文献优化提示词
- [ ] 整合其他价格预测工具
- [ ] UI 界面

## 重要声明
本项目仅用于研究和教育目的，不构成投资建议。投资有风险，决策需谨慎。
  
<br/>

欢迎贡献，包括但不限于**提出 Issue、修复错误、实现新功能、完善文档、本地化**等！  
⭐️⭐️ 如果这个项目对您有帮助，请给我们一个 Star！⭐️⭐️
