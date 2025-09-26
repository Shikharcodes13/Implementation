import requests
import time
from typing import Dict, Any, List, Tuple
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class CustomerAPIClient:
    def __init__(self, api_base_url: str, api_key: str = None, timeout: int = 30):
        self.api_base_url = api_base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST", "GET", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'CSV-Upload-System/1.0'
        })
        
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}'
            })
    
    def create_customer(self, customer_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Create a single customer via API
        
        Returns:
            - success: Boolean indicating success
            - response_data: API response or error details
        """
        try:
            url = f"{self.api_base_url}/customers"
            
            response = self.session.post(
                url,
                json=customer_data,
                timeout=self.timeout
            )
            
            if response.status_code in [200, 201]:
                return True, response.json()
            else:
                # Try to parse JSON error body for clearer diagnostics
                parsed_error = None
                try:
                    parsed_error = response.json()
                except Exception:
                    parsed_error = None

                return False, {
                    'status_code': response.status_code,
                    'endpoint': url,
                    'message': parsed_error.get('message') if isinstance(parsed_error, dict) and 'message' in parsed_error else response.text,
                    'error': parsed_error.get('error') if isinstance(parsed_error, dict) else 'http_error',
                    'response_body': parsed_error if isinstance(parsed_error, dict) else None,
                    'customer_data': customer_data
                }
                
        except requests.exceptions.Timeout:
            return False, {
                'error': 'timeout',
                'message': 'API request timed out',
                'customer_data': customer_data
            }
        except requests.exceptions.ConnectionError:
            return False, {
                'error': 'connection_error',
                'message': 'Failed to connect to API',
                'customer_data': customer_data
            }
        except Exception as e:
            return False, {
                'error': 'unexpected_error',
                'message': str(e),
                'customer_data': customer_data
            }
    
    def create_customers_batch(self, customers: List[Dict[str, Any]], 
                              batch_size: int = 10, 
                              delay_between_batches: float = 0.1) -> Dict[str, Any]:
        """
        Create multiple customers with batching and rate limiting
        
        Args:
            customers: List of customer data
            batch_size: Number of customers to process in each batch
            delay_between_batches: Delay in seconds between batches
        
        Returns:
            Dictionary with results summary
        """
        results = {
            'successful': [],
            'failed': [],
            'total_processed': 0,
            'total_successful': 0,
            'total_failed': 0
        }
        
        # Helper to detect non-customer error-like objects accidentally passed in
        def _looks_like_error_object(obj: Dict[str, Any]) -> bool:
            return isinstance(obj, dict) and obj.get('type') == 'validation_error' and 'row_number' in obj

        # Process in batches
        for i in range(0, len(customers), batch_size):
            batch = customers[i:i + batch_size]
            
            for customer in batch:
                # Guard: skip error objects and mark as failed input
                if _looks_like_error_object(customer):
                    results['failed'].append({
                        'customer_data': customer,
                        'error_details': {
                            'error': 'invalid_input',
                            'message': 'Received error object instead of customer data. Ensure customers = data_transformer.transformed_data',
                            'status_code': None
                        }
                    })
                    results['total_failed'] += 1
                    results['total_processed'] += 1
                    continue

                success, response_data = self.create_customer(customer)
                
                if success:
                    results['successful'].append({
                        'customer_data': customer,
                        'api_response': response_data
                    })
                    results['total_successful'] += 1
                else:
                    results['failed'].append({
                        'customer_data': customer,
                        'error_details': response_data
                    })
                    results['total_failed'] += 1
                
                results['total_processed'] += 1
            
            # Delay between batches to avoid rate limiting
            if i + batch_size < len(customers):
                time.sleep(delay_between_batches)
        
        return results
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test API connection by listing the customers collection."""
        try:
            # For MockAPI.io and similar services, use the collection as health check
            url = f"{self.api_base_url}/customers"
            response = self.session.get(url, timeout=10)
            if response.status_code in (200, 204):
                return True, "API connection successful"
            return False, f"API returned status {response.status_code}"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"

def main(customers: List[Dict[str, Any]], 
         api_base_url: str, 
         api_key: str = None,
         batch_size: int = 10) -> Dict[str, Any]:
    """
    Main function for Windmill integration
    
    Args:
        customers: List of customer data to create
        api_base_url: Base URL of the customer API
        api_key: API key for authentication
        batch_size: Number of customers to process in each batch
    
    Returns:
        Dictionary with API results
    """
    client = CustomerAPIClient(api_base_url, api_key)
    
    # Test connection first
    connection_ok, connection_message = client.test_connection()
    
    if not connection_ok:
        return {
            'success': False,
            'error': 'connection_failed',
            'message': connection_message,
            'results': None
        }
    
    # Create customers
    results = client.create_customers_batch(customers, batch_size)
    
    return {
        'success': True,
        'message': f"Processed {results['total_processed']} customers",
        'results': results
    }

