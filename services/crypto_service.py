import requests
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class CryptoService:
    """Service for fetching cryptocurrency data from CoinGecko API"""
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.timeout = 30
    
    def fetch_top_10_cryptocurrencies(self) -> Optional[List[Dict]]:
        """
        Fetch top 10 cryptocurrencies by market cap from CoinGecko API
        
        Returns:
            List of cryptocurrency data or None if failed
        """
        try:
            url = f"{self.base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 10,
                'page': 1,
                'sparkline': 'false',
                'price_change_percentage': '24h'
            }
            
            logger.info("Fetching top 10 cryptocurrencies from CoinGecko API")
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Transform data to our format
            crypto_list = []
            for coin in data:
                crypto_data = {
                    'id': coin['id'],
                    'name': coin['name'],
                    'symbol': coin['symbol'].upper(),
                    'price_usd': coin['current_price'],
                    'market_cap_usd': coin['market_cap'],
                    'volume_24h_usd': coin['total_volume'],
                    'price_change_24h_percent': coin['price_change_percentage_24h'] or 0,
                    'market_cap_rank': coin['market_cap_rank'],
                    'image_url': coin['image']
                }
                crypto_list.append(crypto_data)
            
            logger.info(f"Successfully fetched {len(crypto_list)} cryptocurrencies")
            return crypto_list
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error when fetching crypto data: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error when fetching crypto data: {str(e)}")
            return None
    
    def get_crypto_by_ids(self, crypto_ids: List[str]) -> Optional[List[Dict]]:
        """
        Fetch specific cryptocurrencies by their IDs
        
        Args:
            crypto_ids: List of cryptocurrency IDs
            
        Returns:
            List of cryptocurrency data or None if failed
        """
        try:
            if not crypto_ids:
                return []
            
            ids_param = ','.join(crypto_ids)
            url = f"{self.base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'ids': ids_param,
                'order': 'market_cap_desc',
                'sparkline': 'false',
                'price_change_percentage': '24h'
            }
            
            logger.info(f"Fetching specific cryptocurrencies: {crypto_ids}")
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Transform data to our format
            crypto_list = []
            for coin in data:
                crypto_data = {
                    'id': coin['id'],
                    'name': coin['name'],
                    'symbol': coin['symbol'].upper(),
                    'price_usd': coin['current_price'],
                    'market_cap_usd': coin['market_cap'],
                    'volume_24h_usd': coin['total_volume'],
                    'price_change_24h_percent': coin['price_change_percentage_24h'] or 0,
                    'market_cap_rank': coin['market_cap_rank'],
                    'image_url': coin['image']
                }
                crypto_list.append(crypto_data)
            
            logger.info(f"Successfully fetched {len(crypto_list)} specific cryptocurrencies")
            return crypto_list
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error when fetching specific crypto data: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error when fetching specific crypto data: {str(e)}")
            return None
