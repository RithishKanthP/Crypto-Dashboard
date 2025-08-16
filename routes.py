from flask import Blueprint, render_template, jsonify, flash
from datetime import datetime, timedelta
import logging
from services.database_service import DatabaseService
from services.crypto_service import CryptoService

main_bp = Blueprint("main", __name__)
logger = logging.getLogger(__name__)


@main_bp.route("/")
def dashboard():
    """Main dashboard page showing top 10 cryptocurrencies"""
    try:
        db_service = DatabaseService()

        # Get latest top 10 data
        latest_data = db_service.get_latest_top_10()

        # Get last update info
        last_update = db_service.get_last_update()

        return render_template(
            "dashboard.html", crypto_data=latest_data, last_update=last_update
        )
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        return render_template("error.html", error="Failed to load cryptocurrency data")


@main_bp.route("/api/crypto-data")
def api_crypto_data():
    """API endpoint for getting current crypto data"""
    try:
        db_service = DatabaseService()
        latest_data = db_service.get_latest_top_10()

        # Format data for JSON response
        formatted_data = []
        for crypto in latest_data:
            formatted_data.append(
                {
                    "id": crypto["crypto_id"],
                    "name": crypto["name"],
                    "symbol": crypto["symbol"],
                    "price": float(crypto["price_usd"]),
                    "market_cap": float(crypto["market_cap_usd"]),
                    "volume_24h": float(crypto["volume_24h_usd"]),
                    "price_change_24h": float(crypto["price_change_24h_percent"]),
                    "rank": crypto["market_cap_rank"],
                    "timestamp": crypto["timestamp"].isoformat(),
                }
            )

        return jsonify({"status": "success", "data": formatted_data})
    except Exception as e:
        logger.error(f"Error in API endpoint: {str(e)}")
        return (
            jsonify(
                {"status": "error", "message": "Failed to fetch cryptocurrency data"}
            ),
            500,
        )


@main_bp.route("/api/refresh")
def api_refresh():
    """Manual refresh endpoint for testing"""
    try:
        crypto_service = CryptoService()
        db_service = DatabaseService()

        # Fetch latest data
        top_10_data = crypto_service.fetch_top_10_cryptocurrencies()

        if top_10_data:
            # Store in database
            db_service.store_crypto_data(top_10_data)

            return jsonify(
                {
                    "status": "success",
                    "message": "Data refreshed successfully",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        else:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Failed to fetch data from CoinGecko API",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Error refreshing data: {str(e)}")
        return jsonify({"status": "error", "message": f"Refresh failed: {str(e)}"}), 500


@main_bp.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})
