# bot-alert-carindustry
Fetches live Tesla news and market data then posts a short summary to Discord.

## Environment variables

- `DISCORD_WEBHOOK` – target Discord webhook URL
- `OPENAI_API_KEY` – API key for OpenAI (used by `main_openai.py`)
- `XAI_API_KEY` – API key for xAI (used by `main_xai.py`)
- `GNEWS_API_KEY` – API token for GNews used to fetch the latest Tesla articles

## Dependencies

The scripts require `openai`, `requests`, `yfinance` and `beautifulsoup4`.
