import os
from datetime import timedelta


class Config:
    """Base configuration class"""

    # Flask Configuration
    SECRET_KEY = os.environ.get("SESSION_SECRET", "crypto-dashboard-default-secret-key")

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://localhost/crypto_dashboard"
    )
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AWS Configuration
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

    # SES Configuration
    SES_FROM_EMAIL = os.environ.get("SES_FROM_EMAIL", "rithishkanth9@gmail.com")
    SES_TO_EMAIL = os.environ.get("SES_TO_EMAIL", "rithishpabbu@gmail.com")

    # CoinGecko API Configuration
    COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
    COINGECKO_API_KEY = os.environ.get("COINGECKO_API_KEY")
    API_REQUEST_TIMEOUT = 30

    # Application Configuration
    TIMEZONE = "America/Chicago"  # CST timezone
    UPDATE_SCHEDULE_HOUR = 9  # 9 AM CST
    UPDATE_SCHEDULE_MINUTE = 0

    # Data Retention
    DATA_RETENTION_DAYS = 30

    # Email Configuration
    ENABLE_EMAIL_NOTIFICATIONS = True

    # Logging Configuration
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    # Redis Configuration (for caching, if needed)
    REDIS_URL = os.environ.get("REDIS_URL")

    # Rate Limiting
    API_RATE_LIMIT = "100 per hour"


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False

    # Enhanced security settings for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


# Configuration mapping
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """Get configuration based on environment"""
    env = os.environ.get("FLASK_ENV", "development")
    return config.get(env, config["default"])
