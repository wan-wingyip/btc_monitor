import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///bitcoin_price.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Bitcoin price monitoring configuration
    BTC_PRICE_THRESHOLD = float(os.getenv('BTC_PRICE_THRESHOLD', '5.0'))  # Default 1% threshold
    BTC_CHECK_INTERVAL = int(os.getenv('BTC_CHECK_INTERVAL', '60'))  # Default check every 60 seconds
    MONITORING_WINDOW = int(os.getenv('MONITORING_WINDOW', '300'))  # Default 5 minutes (300 seconds)
    
    # CoinCap API configuration
    COINCAP_API_URL = os.getenv('COINCAP_API_URL', 'https://api.coincap.io/v2')
    COINCAP_API_KEY = os.getenv('COINCAP_API_KEY', '')  # Optional API key for higher rate limits