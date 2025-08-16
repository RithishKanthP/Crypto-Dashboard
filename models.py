from datetime import datetime
from app import db


class CryptoCurrency(db.Model):
    __tablename__ = "cryptocurrencies"

    id = db.Column(db.String(50), primary_key=True)  # e.g., 'bitcoin'
    name = db.Column(db.String(100), nullable=False)  # e.g., 'Bitcoin'
    symbol = db.Column(db.String(10), nullable=False)  # e.g., 'BTC'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class CryptoData(db.Model):
    __tablename__ = "crypto_data"

    id = db.Column(db.Integer, primary_key=True)
    crypto_id = db.Column(
        db.String(50), db.ForeignKey("cryptocurrencies.id"), nullable=False
    )
    price_usd = db.Column(db.Numeric(20, 8), nullable=False)
    market_cap_usd = db.Column(db.Numeric(20, 2), nullable=False)
    volume_24h_usd = db.Column(db.Numeric(20, 2), nullable=False)
    price_change_24h_percent = db.Column(db.Numeric(10, 4), nullable=False)
    market_cap_rank = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    cryptocurrency = db.relationship("CryptoCurrency", backref="data_points")


class DashboardUpdate(db.Model):
    __tablename__ = "dashboard_updates"

    id = db.Column(db.Integer, primary_key=True)
    update_timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'success', 'failed'
    error_message = db.Column(db.Text)
    email_sent = db.Column(db.Boolean, default=False)
    top_10_data = db.Column(db.JSON)  # Store top 10 snapshot as JSON
