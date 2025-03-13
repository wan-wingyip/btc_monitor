from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class BitcoinPrice(db.Model):
    __tablename__ = 'bitcoin_prices'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    price = db.Column(db.Float, nullable=False)
    price_usd = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<BitcoinPrice {self.timestamp} - ${self.price_usd}>'

class PriceAlert(db.Model):
    __tablename__ = 'price_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    previous_price = db.Column(db.Float, nullable=False)
    percent_change = db.Column(db.Float, nullable=False)
    direction = db.Column(db.String(10), nullable=False)  # "increase" or "decrease"
    
    def __repr__(self):
        return f'<PriceAlert {self.timestamp} - {self.direction} {abs(self.percent_change):.2f}%>'