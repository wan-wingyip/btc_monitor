import requests
import logging
from datetime import datetime, timedelta
from flask import current_app
from .models import db, BitcoinPrice, PriceAlert
from .routes import notify_price_check

logger = logging.getLogger(__name__)

def get_bitcoin_price():
    """
    Fetch the current Bitcoin price from CoinCap API
    Returns a tuple of (price, price_usd)
    """
    api_url = f"{current_app.config['COINCAP_API_URL']}/assets/bitcoin"
    headers = {}
    
    # Add API key if available
    if current_app.config['COINCAP_API_KEY']:
        headers['Authorization'] = f"Bearer {current_app.config['COINCAP_API_KEY']}"
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        price_usd = float(data['data']['priceUsd'])
        
        # Save the price to database
        btc_price = BitcoinPrice(price=price_usd, price_usd=price_usd)
        db.session.add(btc_price)
        db.session.commit()
        
        # Notify clients about the price update
        notify_price_check(current_app)
        
        logger.info(f"Bitcoin price: ${price_usd:.2f}")
        return price_usd
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching Bitcoin price: {e}")
        return None
    except (KeyError, ValueError) as e:
        logger.error(f"Error parsing Bitcoin price data: {e}")
        return None

def check_price_threshold():
    """
    Check if Bitcoin price has changed beyond the threshold in the monitoring window
    """
    threshold = current_app.config['BTC_PRICE_THRESHOLD']
    window = current_app.config['MONITORING_WINDOW']
    
    # Get current price
    current_price = get_bitcoin_price()
    if not current_price:
        return
    
    # Calculate the time range for the monitoring window
    window_start = datetime.utcnow() - timedelta(seconds=window)
    
    # Get the earliest price within the monitoring window
    earliest_price_record = BitcoinPrice.query.filter(
        BitcoinPrice.timestamp >= window_start
    ).order_by(BitcoinPrice.timestamp.asc()).first()
    
    if not earliest_price_record:
        logger.info("Not enough data to compare prices")
        return
    
    # Calculate percentage change
    previous_price = earliest_price_record.price_usd
    percent_change = ((current_price - previous_price) / previous_price) * 100
    
    logger.info(f"Price change in last {window} seconds: {percent_change:.2f}%")
    
    # Check if change exceeds threshold
    if abs(percent_change) >= threshold:
        direction = "increase" if percent_change > 0 else "decrease"
        logger.warning(f"Bitcoin price {direction} alert: {abs(percent_change):.2f}% in {window} seconds")
        
        # Record the alert
        alert = PriceAlert(
            current_price=current_price,
            previous_price=previous_price,
            percent_change=percent_change,
            direction=direction
        )
        db.session.add(alert)
        db.session.commit()
        
        return alert
    
    return None