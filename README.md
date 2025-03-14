# Bitcoin Price Monitor

A Flask-based application that monitors Bitcoin price changes in real-time and generates alerts when price movements exceed configured thresholds.

## Features

- Real-time Bitcoin price monitoring using CoinCap API
- Configurable threshold for price change alerts
- Automatic alerts when Bitcoin price changes exceed the threshold within a monitoring window
- Web dashboard with real-time updates
- API endpoints for programmatic access to price data and alerts
- Docker for easy deployment


## Dashboard

The web dashboard shows:

1. Current Bitcoin price with last update time
2. A table of Bitcoin prices for the last 5 minutes with percentage changes
3. A table of all price alerts triggered by threshold exceedances

## Project Structure

```
btc_monitor/
├── app/
│   ├── __init__.py          # Init Flask application
│   ├── config.py            # Configuration settings
│   ├── models.py            # ORM database models
│   ├── routes.py            # Flask Routes and API endpoints
│   ├── services.py          # BTC Price checking function
│   ├── templates/           # HTML templates
│   │   ├── index.html       # Dashboard template
│   │   └── layout.html      # Base layout template
│   └── static/              # Static assets
│       └── main.js          # JavaScript for real-time updates
├── migrations/              # Database migrations
├── Dockerfile               # Docker file for image creation
├── docker-compose.yml       # Docker Compose configuration
├── .env                     # Env variables
├── requirements.txt         # Python dependencies
└── run.py                   # Application entry point
```

## Requirements

- Python 3.8 or higher
- Flask and extensions (see requirements.txt)
- Docker (optional, for containerized deployment)

## Configuration

Environment variables set in `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URI` | Database connection string | `sqlite:///bitcoin_price.db` |
| `BTC_PRICE_THRESHOLD` | Percentage change that triggers an alert | `2.0` |
| `BTC_CHECK_INTERVAL` | How often to check the price (seconds) | `60` |
| `MONITORING_WINDOW` | Time window for comparison (seconds) | `300` (5 minutes) |
| `COINCAP_API_URL` | CoinCap API base URL | `https://api.coincap.io/v2` |
| `COINCAP_API_KEY` | Optional CoinCap API key for higher rate limits | ` ` |

## Installation and Setup

### Using Docker

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd bitcoin-price-monitor
   ```

2. Modify the `.env` file with your desired settings.

3. Build and start the Docker container:
   ```bash
   docker-compose up -d
   ```

4. Access the dashboard at http://localhost:5000

5. View logs:
   ```bash
   docker-compose logs -f
   ```

6. Stop the application:
   ```bash
   docker-compose down
   ```

### Running Locally

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd btc_monitor
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Modify the `.env` file with your desired settings.

5. Run the application:
   ```bash
   python run.py
   ```

6. Access the dashboard at http://localhost:5000

## Potential API Endpoints

The application provides the following API endpoints:

- `GET /health` - Health check
- `GET /api/prices` - Get prices for the last monitoring window
- `GET /api/alerts` - Get all price alerts
- `GET /api/stream` - Server-sent events endpoint for real-time updates
- `GET /config` - Get current monitoring configuration

