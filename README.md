# 📈 Financial Market Analysis & Distribution System

A sophisticated AI-powered system that automates financial market analysis, generates comprehensive reports, and distributes them via Telegram. Built with CrewAI for agent orchestration and supporting multiple languages.

## ✨ Features

- **Automated Data Collection**
  - Real-time financial news aggregation
  - Market data collection from multiple sources
  - Web search integration for comprehensive coverage

- **AI-Powered Analysis**
  - Intelligent summarization of market trends
  - Sentiment analysis of market conditions
  - Key insights extraction from financial data

- **Multilingual Support**
  - Native support for English, Arabic, Hindi, and Hebrew
  - Automatic content translation
  - Locale-specific formatting

- **Visual Intelligence**
  - Automated chart generation
  - Market trend visualizations
  - Performance heatmaps

- **Smart Distribution**
  - Telegram channel integration
  - Scheduled reporting
  - Error-resilient delivery system

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Required API Keys:
  - Google Gemini API Key
  - Tavily API Key
  - Telegram Bot Token
  - Telegram Channel ID

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/CrewAIAgent.git
   cd CrewAIAgent
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # OR
   .\.venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

## 📹 Video Demonstration

Watch a quick demo of the system in action:

```
assets/2025-09-03 21-24-17.mkv
```

### How to view the demo:
1. Clone the repository
2. Open the video file located at `assets/2025-09-03 21-24-17.mkv` in any media player that supports .mkv format (like VLC, Windows Media Player, or QuickTime with additional codecs)

### What's shown in the demo:
- System initialization and configuration
- Real-time market data collection
- AI-powered analysis and summarization
- Multi-language report generation
- Telegram distribution

## 🛠️ Configuration

Edit the `.env` file with your configuration:

```ini
# Required API Keys
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHANNEL_ID=your_telegram_channel_id

# Optional Settings
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
CACHE_DIR=./.cache
OUTPUT_DIR=./output
```

## 🚦 Usage

### Running the System

```bash
python financial_market_crew.py
```

### Output

The system will generate:
1. Market summary in English
2. Translated versions (if configured)
3. Log files for debugging

## 🏗️ Project Structure

```
CrewAIAgent/
├── .env                    # Environment configuration
├── .env.example            # Example configuration
├── pyproject.toml          # Project metadata
├── requirements.txt        # Dependencies
├── financial_market_crew.py  # Main application
├── .cache/                 # Cached data (auto-created)
└── output/                 # Generated text reports (auto-created)
```

## 🔍 Advanced Usage

### Customizing Market Analysis

Edit `financial_market_crew.py` to modify:
- Search queries
- Analysis parameters
- Output formats
- Distribution settings

### Logging

Logs are stored in `financial_market_crew.log` with different verbosity levels based on your `LOG_LEVEL` setting.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [CrewAI](https://www.crewai.com/)
- Powered by Google Gemini
- Data from Tavily Search API
