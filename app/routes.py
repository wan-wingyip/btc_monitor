from datetime import datetime, timedelta
from flask import jsonify, render_template, Response, current_app
from .models import BitcoinPrice, PriceAlert, db
import json
import time
import queue

# Queue for server-sent events
event_queue = queue.Queue()

# Create a list to store price check callbacks
# This needs to be module-level so it's accessible from both routes and services
price_check_callbacks = []

def notify_price_check(app):
    """Notify all clients that a new price check has occurred"""
    for callback in price_check_callbacks:
        try:
            callback()
        except Exception as e:
            app.logger.error(f"Error notifying client: {e}")

def register_routes(app):
    
    @app.route('/')
    def index():
        """Home page with Bitcoin price data"""
        # Get configuration
        threshold = current_app.config['BTC_PRICE_THRESHOLD']
        interval = current_app.config['BTC_CHECK_INTERVAL']
        window = current_app.config['MONITORING_WINDOW']
        
        # Calculate time range for the last window seconds
        window_start = datetime.utcnow() - timedelta(seconds=window)
        
        # Get prices from the last window seconds
        prices = BitcoinPrice.query.filter(
            BitcoinPrice.timestamp >= window_start
        ).order_by(BitcoinPrice.timestamp.desc()).all()
        
        # Get all alerts
        alerts = PriceAlert.query.order_by(PriceAlert.timestamp.desc()).all()
        
        return render_template(
            'index.html',
            prices=prices,
            alerts=alerts,
            threshold=threshold,
            interval=interval
        )
    
    @app.route('/api/prices')
    def get_prices():
        """API endpoint to get prices for the monitoring window"""
        window = current_app.config['MONITORING_WINDOW']
        window_start = datetime.utcnow() - timedelta(seconds=window)
        
        prices = BitcoinPrice.query.filter(
            BitcoinPrice.timestamp >= window_start
        ).order_by(BitcoinPrice.timestamp.desc()).all()
        
        return jsonify({
            "prices": [
                {
                    "timestamp": price.timestamp,
                    "price_usd": price.price_usd
                }
                for price in prices
            ]
        })
    
    @app.route('/api/alerts')
    def get_alerts():
        """API endpoint to get all price alerts"""
        alerts = PriceAlert.query.order_by(PriceAlert.timestamp.desc()).all()
        
        return jsonify({
            "alerts": [
                {
                    "timestamp": alert.timestamp,
                    "current_price": alert.current_price,
                    "previous_price": alert.previous_price,
                    "percent_change": alert.percent_change,
                    "direction": alert.direction
                }
                for alert in alerts
            ]
        })
    
    @app.route('/api/stream')
    def event_stream():
        """Server-sent events endpoint for real-time updates"""
        def generate():
            # Send a test message to establish the connection
            yield "data: {\"type\": \"connected\"}\n\n"
            
            # Create a client-specific queue
            client_queue = queue.Queue()
            
            # Function to be called when a new price is checked
            def price_checked():
                client_queue.put(json.dumps({"type": "price_update"}))
            
            # Register this client's queue
            price_check_callbacks.append(price_checked)
            
            try:
                while True:
                    # Wait for data and send it to the client
                    try:
                        data = client_queue.get(timeout=30)
                        yield f"data: {data}\n\n"
                    except queue.Empty:
                        # Send a keepalive message every 30 seconds
                        yield "data: {\"type\": \"keepalive\"}\n\n"
            finally:
                # Remove callback when client disconnects
                if price_checked in price_check_callbacks:
                    price_check_callbacks.remove(price_checked)
        
        return Response(generate(), mimetype="text/event-stream")
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({"status": "ok"})
    
    @app.route('/config')
    def get_config():
        """Get the current monitoring configuration"""
        return jsonify({
            "threshold_percent": app.config['BTC_PRICE_THRESHOLD'],
            "check_interval_seconds": app.config['BTC_CHECK_INTERVAL'],
            "monitoring_window_seconds": app.config['MONITORING_WINDOW']
        })