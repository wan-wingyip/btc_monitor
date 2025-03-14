import logging
from flask import Flask
from flask_migrate import Migrate
from flask_apscheduler import APScheduler
from .config import Config
from .models import db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize scheduler
scheduler = APScheduler()

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    scheduler.init_app(app)
    
    # Register routes
    from .routes import register_routes
    register_routes(app)
    
    # Start scheduler
    with app.app_context():
        from .services import check_price_threshold
        
        # Create database tables
        db.create_all()
        
        # Create a wrapper function that runs in app context
        def check_price_with_app_context():
            with app.app_context():
                check_price_threshold()
        
        # Add jobs to scheduler
        scheduler.add_job(
            id='check_bitcoin_price',
            func=check_price_with_app_context,
            trigger='interval',
            seconds=app.config['BTC_CHECK_INTERVAL']
        )
        
        scheduler.start()
    
    return app