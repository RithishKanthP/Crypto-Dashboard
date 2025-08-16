import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


def create_app():
    # create the app
    app = Flask(__name__)
    app.secret_key = os.environ.get(
        "SESSION_SECRET", "crypto-dashboard-default-secret-key"
    )
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # configure the database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        "postgresql://rithish:rithish@localhost:5432/crypto_dashboard",
    )
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    # AWS Configuration
    app.config["AWS_REGION"] = os.environ.get("AWS_REGION", "us-east-2")
    app.config["SES_FROM_EMAIL"] = os.environ.get(
        "SES_FROM_EMAIL", "rithishkanth9@gmail.com"
    )
    app.config["SES_TO_EMAIL"] = os.environ.get(
        "SES_TO_EMAIL", "rithishpabbu@gmail.com"
    )

    # initialize the app with the extension
    db.init_app(app)

    with app.app_context():
        # Import models to ensure tables are created
        import models

        db.create_all()

        # Register routes
        from routes import main_bp

        app.register_blueprint(main_bp)

    return app


# Create app instance
app = create_app()
