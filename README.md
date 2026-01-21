# WEEX AI AI Trading Bot

This is an advanced AI-powered trading bot designed for the WEEX exchange. It leverages machine learning models to analyze market data, manage risk, and execute trades autonomously.

## Features

- **AI Decision Engine**: Uses advanced ML models to predict market movements.
- **Risk Management**: Comprehensive guardrails including max drawdown, stiff stop-losses, and position sizing.
- **Automated Execution**: Efficient order placement and management on WEEX.
- **Real-time Monitoring**: Logging and telemetry for live trade monitoring.

## Prerequisities

- Python 3.9+
- WEEX Account API Keys

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd Trade-Bot
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # Windows
    .\.venv\Scripts\activate
    # Linux/Mac
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  **Environment Variables:**
    Create a `.env` file in the root directory and add your API credentials:
    ```env
    WEEX_API_KEY=your_api_key
    WEEX_SECRET_KEY=your_secret_key
    WEEX_PASSPHRASE=your_passphrase
    OPENAI_API_KEY=your_openai_api_key
    # Add other necessary env vars
    ```

2.  **Settings:**
    Adjust trading parameters in `config/settings.yaml`.

## Usage

To start the trading bot:

```bash
python main.py
```

## Docker

Build the image:

```bash
docker build -t trade-bot .
```

Run with environment variables (recommended to use an env file):

```bash
docker run --rm --env-file .env trade-bot
```

To run the verification suite:

```bash
python validate_production.py
```

## Structure

- `ai/`: AI models and logic.
- `exchange/`: Exchange connectivity (WEEX).
- `strategy/`: Trading strategies and decision engine.
- `risk/`: Risk management and guardrails.
- `config/`: Configuration files.
- `utils/`: Helper utilities.

## Disclaimer

Trading cryptocurrencies involves significant risk and can result in the loss of your capital. This bot is provided for educational and experimental purposes. Use at your own risk.
