import boto3
import logging
from datetime import datetime
from typing import List, Dict, Optional
from botocore.exceptions import ClientError, NoCredentialsError
import os

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via AWS SES"""

    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-2")
        self.from_email = os.environ.get(
            "SES_FROM_EMAIL", "rithishkanth9@gmail.com.com"
        )
        self.to_email = os.environ.get("SES_TO_EMAIL", "rithishpabbu@gmail.com")

        try:
            self.ses_client = boto3.client("ses", region_name=self.region)
        except Exception as e:
            logger.error(f"Failed to initialize SES client: {str(e)}")
            self.ses_client = None

    def send_daily_dashboard_email(self, crypto_data: List[Dict]) -> bool:
        """
        Send daily dashboard email with top 10 cryptocurrencies

        Args:
            crypto_data: List of cryptocurrency data

        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.ses_client:
            logger.error("SES client not initialized")
            return False

        try:
            subject = f"Daily Crypto Dashboard - Top 10 - {datetime.now().strftime('%Y-%m-%d')}"

            # Generate HTML and text content
            html_content = self._generate_email_html(crypto_data)
            text_content = self._generate_email_text(crypto_data)

            response = self.ses_client.send_email(
                Source=self.from_email,
                Destination={"ToAddresses": [self.to_email]},
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {
                        "Html": {"Data": html_content, "Charset": "UTF-8"},
                        "Text": {"Data": text_content, "Charset": "UTF-8"},
                    },
                },
            )

            logger.info(
                f"Email sent successfully to {self.to_email}. Message ID: {response['MessageId']}"
            )
            return True

        except ClientError as e:
            logger.error(f"AWS SES ClientError: {e.response['Error']['Message']}")
            return False
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while sending email: {str(e)}")
            return False

    def send_error_notification(self, error_message: str) -> bool:
        """
        Send error notification email

        Args:
            error_message: Error message to include in email

        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.ses_client:
            logger.error("SES client not initialized")
            return False

        try:
            subject = f"Crypto Dashboard Error - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            html_content = f"""
            <html>
            <body>
                <h2>Crypto Dashboard Error Alert</h2>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                <p><strong>Error:</strong></p>
                <pre>{error_message}</pre>
                <p>Please check the application logs for more details.</p>
            </body>
            </html>
            """

            text_content = f"""
            Crypto Dashboard Error Alert
            
            Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
            Error: {error_message}
            
            Please check the application logs for more details.
            """

            response = self.ses_client.send_email(
                Source=self.from_email,
                Destination={"ToAddresses": [self.to_email]},
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {
                        "Html": {"Data": html_content, "Charset": "UTF-8"},
                        "Text": {"Data": text_content, "Charset": "UTF-8"},
                    },
                },
            )

            logger.info(
                f"Error notification email sent. Message ID: {response['MessageId']}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to send error notification: {str(e)}")
            return False

    def _generate_email_html(self, crypto_data: List[Dict]) -> str:
        """Generate HTML content for the email"""

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                .crypto-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                .crypto-table th, .crypto-table td {{ 
                    padding: 12px; 
                    text-align: left; 
                    border-bottom: 1px solid #ddd; 
                }}
                .crypto-table th {{ 
                    background-color: #f8f9fa; 
                    font-weight: bold;
                }}
                .positive {{ color: #28a745; }}
                .negative {{ color: #dc3545; }}
                .rank {{ font-weight: bold; color: #6c757d; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #6c757d; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Daily Cryptocurrency Dashboard</h1>
                <p>Top 10 Cryptocurrencies by Market Cap - {datetime.now().strftime('%B %d, %Y')}</p>
            </div>
            
            <table class="crypto-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Name</th>
                        <th>Symbol</th>
                        <th>Price (USD)</th>
                        <th>24h Change</th>
                        <th>Market Cap</th>
                        <th>Volume (24h)</th>
                    </tr>
                </thead>
                <tbody>
        """

        for crypto in crypto_data:
            change_class = (
                "positive" if crypto["price_change_24h_percent"] >= 0 else "negative"
            )
            change_symbol = "+" if crypto["price_change_24h_percent"] >= 0 else ""

            html += f"""
                    <tr>
                        <td class="rank">#{crypto['market_cap_rank']}</td>
                        <td><strong>{crypto['name']}</strong></td>
                        <td>{crypto['symbol']}</td>
                        <td>${crypto['price_usd']:,.4f}</td>
                        <td class="{change_class}">{change_symbol}{crypto['price_change_24h_percent']:.2f}%</td>
                        <td>${crypto['market_cap_usd']:,.0f}</td>
                        <td>${crypto['volume_24h_usd']:,.0f}</td>
                    </tr>
            """

        html += """
                </tbody>
            </table>
            
            <div class="footer">
                <p>Data provided by CoinGecko API</p>
                <p>This is an automated email from your Crypto Dashboard application.</p>
            </div>
        </body>
        </html>
        """

        return html

    def _generate_email_text(self, crypto_data: List[Dict]) -> str:
        """Generate plain text content for the email"""

        text = f"""
Daily Cryptocurrency Dashboard
Top 10 Cryptocurrencies by Market Cap - {datetime.now().strftime('%B %d, %Y')}

Rank | Name           | Symbol | Price (USD)  | 24h Change | Market Cap      | Volume (24h)
-----|----------------|--------|--------------|------------|-----------------|-------------
"""

        for crypto in crypto_data:
            change_symbol = "+" if crypto["price_change_24h_percent"] >= 0 else ""
            text += f"{crypto['market_cap_rank']:4} | {crypto['name'][:14]:<14} | {crypto['symbol'][:6]:<6} | ${crypto['price_usd']:10,.4f} | {change_symbol}{crypto['price_change_24h_percent']:8.2f}% | ${crypto['market_cap_usd']:13,.0f} | ${crypto['volume_24h_usd']:11,.0f}\n"

        text += """

Data provided by CoinGecko API
This is an automated email from your Crypto Dashboard application.
        """

        return text
