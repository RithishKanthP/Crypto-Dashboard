from sqlalchemy import text, desc
from datetime import datetime, timedelta
import logging
import json
import traceback
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for database operations"""

    def __init__(self):
        # Import here to avoid circular imports
        from app import db
        from models import CryptoCurrency, CryptoData, DashboardUpdate

        self.db = db
        self.CryptoCurrency = CryptoCurrency
        self.CryptoData = CryptoData
        self.DashboardUpdate = DashboardUpdate

    def store_crypto_data(self, crypto_list: List[Dict]) -> bool:
        """
        Store cryptocurrency data in the database

        Args:
            crypto_list: List of cryptocurrency data

        Returns:
            True if stored successfully, False otherwise
        """
        try:
            timestamp = datetime.utcnow()

            # Fetch existing cryptocurrencies in bulk
            existing_cryptos = {
                crypto.id: crypto
                for crypto in self.CryptoCurrency.query.filter(
                    self.CryptoCurrency.id.in_([crypto["id"] for crypto in crypto_list])
                ).all()
            }

            new_crypto_data_list = []

            for crypto in crypto_list:
                if crypto["id"] not in existing_cryptos:
                    new_crypto = self.CryptoCurrency(
                        id=crypto["id"], name=crypto["name"], symbol=crypto["symbol"]
                    )
                    self.db.session.add(new_crypto)
                else:
                    existing_crypto = existing_cryptos[crypto["id"]]
                    existing_crypto.name = crypto["name"]
                    existing_crypto.symbol = crypto["symbol"]
                    existing_crypto.updated_at = timestamp

                # Add new data point
                new_crypto_data = self.CryptoData(
                    crypto_id=crypto["id"],
                    price_usd=crypto["price_usd"],
                    market_cap_usd=crypto["market_cap_usd"],
                    volume_24h_usd=crypto["volume_24h_usd"],
                    price_change_24h_percent=crypto["price_change_24h_percent"],
                    market_cap_rank=crypto["market_cap_rank"],
                    timestamp=timestamp,
                )
                new_crypto_data_list.append(new_crypto_data)

            # Bulk insert new data points (safer to use add_all)
            self.db.session.add_all(new_crypto_data_list)

            self.db.session.commit()

            logger.info(
                f"Successfully stored data for {len(crypto_list)} cryptocurrencies"
            )
            return True

        except Exception as e:
            logger.error(f"Error storing crypto data: {str(e)}")
            logger.debug(traceback.format_exc())
            self.db.session.rollback()
            return False

    def get_latest_top_10(self) -> List[Dict]:
        """
        Get the latest top 10 cryptocurrencies data

        Returns:
            List of cryptocurrency data dictionaries
        """
        try:
            # Get the latest timestamp
            latest_timestamp_query = (
                self.db.session.query(self.CryptoData.timestamp)
                .order_by(desc(self.CryptoData.timestamp))
                .limit(1)
            )
            latest_timestamp = latest_timestamp_query.scalar()

            if not latest_timestamp:
                logger.warning("No cryptocurrency data found in database")
                return []

            # Get top 10 from the latest timestamp
            query = (
                self.db.session.query(
                    self.CryptoData.crypto_id,
                    self.CryptoCurrency.name,
                    self.CryptoCurrency.symbol,
                    self.CryptoData.price_usd,
                    self.CryptoData.market_cap_usd,
                    self.CryptoData.volume_24h_usd,
                    self.CryptoData.price_change_24h_percent,
                    self.CryptoData.market_cap_rank,
                    self.CryptoData.timestamp,
                )
                .join(
                    self.CryptoCurrency,
                    self.CryptoData.crypto_id == self.CryptoCurrency.id,
                )
                .filter(self.CryptoData.timestamp == latest_timestamp)
                .order_by(self.CryptoData.market_cap_rank)
                .limit(10)
            )

            results = query.all()

            crypto_list = []
            for row in results:
                crypto_data = {
                    "crypto_id": row.crypto_id,
                    "name": row.name,
                    "symbol": row.symbol,
                    "price_usd": row.price_usd,
                    "market_cap_usd": row.market_cap_usd,
                    "volume_24h_usd": row.volume_24h_usd,
                    "price_change_24h_percent": row.price_change_24h_percent,
                    "market_cap_rank": row.market_cap_rank,
                    "timestamp": row.timestamp,
                }
                crypto_list.append(crypto_data)

            logger.info(
                f"Retrieved {len(crypto_list)} cryptocurrencies from latest data"
            )
            return crypto_list

        except Exception as e:
            logger.error(f"Error retrieving latest top 10: {str(e)}")
            return []

    def get_last_update(self) -> Optional[Dict]:
        """
        Get information about the last dashboard update

        Returns:
            Dictionary with last update info or None
        """
        try:
            last_update = self.DashboardUpdate.query.order_by(
                desc(self.DashboardUpdate.update_timestamp)
            ).first()

            if not last_update:
                return None

            return {
                "timestamp": last_update.update_timestamp,
                "status": last_update.status,
                "error_message": last_update.error_message,
                "email_sent": last_update.email_sent,
            }

        except Exception as e:
            logger.error(f"Error retrieving last update info: {str(e)}")
            return None

    def log_dashboard_update(
        self,
        status: str,
        error_message: str = None,
        email_sent: bool = False,
        top_10_data: List[Dict] = None,
    ) -> bool:
        """
        Log a dashboard update event

        Args:
            status: Update status ('success' or 'failed')
            error_message: Error message if failed
            email_sent: Whether email was sent
            top_10_data: Top 10 snapshot data

        Returns:
            True if logged successfully, False otherwise
        """
        try:
            update_log = self.DashboardUpdate(
                status=status,
                error_message=error_message,
                email_sent=email_sent,
                top_10_data=json.dumps(top_10_data) if top_10_data else None,
            )

            self.db.session.add(update_log)
            self.db.session.commit()

            logger.info(f"Dashboard update logged: {status}")
            return True

        except Exception as e:
            logger.error(f"Error logging dashboard update: {str(e)}")
            self.db.session.rollback()
            return False

    def get_historical_data(self, crypto_id: str, days: int = 7) -> List[Dict]:
        """
        Get historical data for a specific cryptocurrency

        Args:
            crypto_id: Cryptocurrency ID
            days: Number of days to retrieve

        Returns:
            List of historical data points
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            query = (
                self.db.session.query(self.CryptoData)
                .filter(
                    self.CryptoData.crypto_id == crypto_id,
                    self.CryptoData.timestamp >= start_date,
                )
                .order_by(self.CryptoData.timestamp)
            )

            results = query.all()

            historical_data = []
            for data_point in results:
                historical_data.append(
                    {
                        "timestamp": data_point.timestamp,
                        "price_usd": (
                            float(data_point.price_usd)
                            if data_point.price_usd
                            else None
                        ),
                        "market_cap_usd": (
                            float(data_point.market_cap_usd)
                            if data_point.market_cap_usd
                            else None
                        ),
                        "volume_24h_usd": (
                            float(data_point.volume_24h_usd)
                            if data_point.volume_24h_usd
                            else None
                        ),
                        "price_change_24h_percent": (
                            float(data_point.price_change_24h_percent)
                            if data_point.price_change_24h_percent
                            else None
                        ),
                    }
                )

            return historical_data

        except Exception as e:
            logger.error(f"Error retrieving historical data for {crypto_id}: {str(e)}")
            return []

    def cleanup_old_data(self, days_to_keep: int = 30) -> bool:
        """
        Clean up old data points to manage database size

        Args:
            days_to_keep: Number of days of data to keep

        Returns:
            True if cleanup successful, False otherwise
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

            # Delete old crypto data
            deleted_crypto_data = (
                self.db.session.query(self.CryptoData)
                .filter(self.CryptoData.timestamp < cutoff_date)
                .delete(synchronize_session=False)
            )

            # Delete old dashboard updates
            deleted_updates = (
                self.db.session.query(self.DashboardUpdate)
                .filter(self.DashboardUpdate.update_timestamp < cutoff_date)
                .delete(synchronize_session=False)
            )

            self.db.session.commit()

            logger.info(
                f"Cleanup completed: removed {deleted_crypto_data} crypto data points and {deleted_updates} update logs"
            )
            return True

        except Exception as e:
            logger.error(f"Error during data cleanup: {str(e)}")
            self.db.session.rollback()
            return False
