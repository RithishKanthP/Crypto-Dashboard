import json
import logging
from datetime import datetime
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging for Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Add current directory to path for imports
sys.path.append("/var/task")


def lambda_handler(event, context):
    """
    AWS Lambda function handler for scheduled cryptocurrency data updates
    """
    try:
        logger.info("Starting cryptocurrency dashboard update")

        # Import services (after path setup)
        from app import app  # Import your Flask app
        from services.crypto_service import CryptoService
        from services.email_service import EmailService
        from services.database_service import DatabaseService

        # Initialize services
        crypto_service = CryptoService()
        email_service = EmailService()
        db_service = DatabaseService()

        # Use Flask app context
        with app.app_context():
            # Fetch latest cryptocurrency data
            logger.info("Fetching top 10 cryptocurrencies from CoinGecko API")
            crypto_data = crypto_service.fetch_top_10_cryptocurrencies()

            if not crypto_data:
                error_msg = "Failed to fetch cryptocurrency data from CoinGecko API"
                logger.error(error_msg)

                # Log failed update
                db_service.log_dashboard_update(
                    status="failed", error_message=error_msg, email_sent=False
                )

                # Send error notification
                email_service.send_error_notification(error_msg)

                return {
                    "statusCode": 500,
                    "body": json.dumps({"status": "error", "message": error_msg}),
                }

            # Store data in database
            logger.info("Storing cryptocurrency data in database")
            storage_success = db_service.store_crypto_data(crypto_data)

            if not storage_success:
                error_msg = "Failed to store cryptocurrency data in database"
                logger.error(error_msg)

                # Log failed update
                db_service.log_dashboard_update(
                    status="failed", error_message=error_msg, email_sent=False
                )

                # Send error notification
                email_service.send_error_notification(error_msg)

                return {
                    "statusCode": 500,
                    "body": json.dumps({"status": "error", "message": error_msg}),
                }

            # Send daily dashboard email
            logger.info("Sending daily dashboard email")
            email_sent = email_service.send_daily_dashboard_email(crypto_data)

            # Log successful update
            db_service.log_dashboard_update(
                status="success", error_message=None, email_sent=email_sent
            )

            logger.info("Cryptocurrency dashboard update completed successfully")
            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "status": "success",
                        "message": "Dashboard updated successfully",
                        "timestamp": datetime.utcnow().isoformat(),
                        "cryptocurrencies_updated": len(crypto_data),
                        "email_sent": email_sent,
                    }
                ),
            }

    except Exception as e:
        logger.error(f"Unexpected error in Lambda function: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "status": "error",
                    "message": f"Unexpected error in Lambda function: {str(e)}",
                }
            ),
        }


# For testing the Lambda function locally
if __name__ == "__main__":
    # Mock event and context for local testing
    test_event = {}
    test_context = type(
        "Context",
        (),
        {
            "function_name": "crypto-dashboard-updater",
            "memory_limit_in_mb": 128,
            "invoked_function_arn": "arn:aws:lambda:us-east-2:123456789012:function:crypto-dashboard-updater",
            "aws_request_id": "test-request-id",
        },
    )()

    result = lambda_handler(test_event, test_context)
    print(json.dumps(result, indent=2))
