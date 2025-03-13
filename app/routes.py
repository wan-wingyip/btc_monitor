from flask import jsonify
from .models import BitcoinPrice, PriceAlert

def register_routes(app):
    
    @app.route('/health')
    def health_check():
        return jsonify({"status": "ok"})
    
    @app.route('/price/current')
    def current_price():
        """Get the most recent Bitcoin price"""
        latest_price = BitcoinPrice.query.order_by(BitcoinPrice.timestamp.desc()).first()
        
        if latest_price:
            return jsonify({
                "timestamp": latest_price.timestamp,
                "price_usd": latest_price.price_usd
            })
        else:
            return jsonify({"error": "No price data available"}), 404
    
    @app.route('/alerts')
    def get_alerts():
        """Get all price alerts"""
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
    
    @app.route('/config')
    def get_config():
        """Get the current monitoring configuration"""
        return jsonify({
            "threshold_percent": app.config['BTC_PRICE_THRESHOLD'],
            "check_interval_seconds": app.config['BTC_CHECK_INTERVAL'],
            "monitoring_window_seconds": app.config['MONITORING_WINDOW']
        })