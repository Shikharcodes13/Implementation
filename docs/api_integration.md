# API Integration Guide

This guide covers how to integrate the CSV Upload System with various API endpoints for customer creation.

## Overview

The system supports multiple API integration patterns:
- RESTful APIs with JSON payloads
- Authentication via API keys or bearer tokens
- Retry logic and error handling
- Batch processing with rate limiting

## Configuration

### Basic API Configuration

Edit `config/api_config.json` to configure your API endpoints:

```json
{
  "mock_api": {
    "base_url": "https://jsonplaceholder.typicode.com",
    "endpoints": {
      "customers": "/users",
      "health": "/posts/1"
    },
    "authentication": {
      "type": "bearer_token",
      "api_key": "your-api-key-here"
    },
    "settings": {
      "timeout": 30,
      "batch_size": 10,
      "retry_attempts": 3
    }
  }
}
```

## Supported API Types

### 1. RESTful JSON APIs

Most modern APIs follow REST conventions:

```json
{
  "base_url": "https://api.yourcrm.com/v1",
  "endpoints": {
    "customers": "/customers",
    "health": "/health"
  },
  "authentication": {
    "type": "bearer_token",
    "bearer_token": "your-jwt-token"
  }
}
```

### 2. API Key Authentication

For APIs using API key authentication:

```json
{
  "authentication": {
    "type": "api_key",
    "api_key": "your-api-key",
    "header_name": "X-API-Key"
  }
}
```

### 3. Basic Authentication

For APIs using basic auth:

```json
{
  "authentication": {
    "type": "basic",
    "username": "your-username",
    "password": "your-password"
  }
}
```

## Mock API Services

For testing and development, you can use these free mock API services:

### JSONPlaceholder (Recommended for Testing)
```json
{
  "base_url": "https://jsonplaceholder.typicode.com",
  "endpoints": {
    "customers": "/users",
    "health": "/posts/1"
  }
}
```

### Reqres.in
```json
{
  "base_url": "https://reqres.in/api",
  "endpoints": {
    "customers": "/users",
    "health": "/users/1"
  }
}
```

### HTTPBin (For Testing HTTP Requests)
```json
{
  "base_url": "https://httpbin.org",
  "endpoints": {
    "customers": "/post",
    "health": "/status/200"
  }
}
```

## Creating a Mock API in Windmill

You can create a mock API directly in Windmill for testing:

### Simple Mock Customer API

Create a new script in Windmill called `mock_customer_api`:

```python
def main(customer_data: dict) -> dict:
    """Mock API endpoint for customer creation"""
    import hashlib
    import json
    from datetime import datetime
    
    # Generate a mock customer ID
    customer_json = json.dumps(customer_data, sort_keys=True)
    customer_id = hashlib.md5(customer_json.encode()).hexdigest()[:8]
    
    # Return mock response
    return {
        "id": f"cust_{customer_id}",
        "status": "created",
        "data": customer_data,
        "created_at": datetime.now().isoformat(),
        "api_version": "1.0"
    }
```

### Advanced Mock API with Validation

```python
def main(customer_data: dict) -> dict:
    """Advanced mock API with validation and error simulation"""
    import random
    import hashlib
    import json
    from datetime import datetime
    
    # Simulate random failures (10% failure rate)
    if random.random() < 0.1:
        return {
            "error": "api_error",
            "message": "Simulated API failure",
            "status_code": 500
        }
    
    # Validate required fields
    required_fields = ['name', 'email']
    missing_fields = [field for field in required_fields if not customer_data.get(field)]
    
    if missing_fields:
        return {
            "error": "validation_error",
            "message": f"Missing required fields: {', '.join(missing_fields)}",
            "status_code": 400
        }
    
    # Create customer
    customer_json = json.dumps(customer_data, sort_keys=True)
    customer_id = hashlib.md5(customer_json.encode()).hexdigest()[:8]
    
    return {
        "id": f"cust_{customer_id}",
        "status": "created",
        "data": customer_data,
        "created_at": datetime.now().isoformat(),
        "api_version": "1.0"
    }
```

## Error Handling

### HTTP Status Codes

The system handles various HTTP status codes:

- **200/201**: Success
- **400**: Bad Request (validation errors)
- **401**: Unauthorized (authentication issues)
- **429**: Too Many Requests (rate limiting)
- **500/502/503/504**: Server errors (will retry)

### Retry Logic

Configure retry behavior:

```json
{
  "settings": {
    "retry_attempts": 3,
    "backoff_factor": 1,
    "retry_on_status": [429, 500, 502, 503, 504]
  }
}
```

### Custom Error Handling

Add custom error handling in the API client:

```python
def handle_api_error(self, response, customer_data):
    """Custom error handling logic"""
    if response.status_code == 409:
        # Handle duplicate customer
        return {
            'error': 'duplicate_customer',
            'message': 'Customer already exists',
            'customer_data': customer_data
        }
    elif response.status_code == 422:
        # Handle validation errors
        return {
            'error': 'validation_failed',
            'message': 'Customer data validation failed',
            'details': response.json(),
            'customer_data': customer_data
        }
    else:
        # Default error handling
        return {
            'error': 'api_error',
            'message': f'API returned status {response.status_code}',
            'customer_data': customer_data
        }
```

## Rate Limiting

### Batch Processing

Control API call rate with batch processing:

```json
{
  "settings": {
    "batch_size": 10,
    "delay_between_batches": 0.5,
    "max_concurrent_requests": 5
  }
}
```

### Adaptive Rate Limiting

Implement adaptive rate limiting:

```python
def adaptive_delay(self, response_time: float, success_rate: float) -> float:
    """Calculate adaptive delay based on API performance"""
    base_delay = 0.1
    
    # Increase delay if response time is slow
    if response_time > 2.0:
        base_delay *= 2
    
    # Increase delay if success rate is low
    if success_rate < 0.8:
        base_delay *= 1.5
    
    return min(base_delay, 2.0)  # Cap at 2 seconds
```

## Authentication

### Bearer Token Authentication

```python
def setup_bearer_auth(self, token: str):
    """Setup bearer token authentication"""
    self.session.headers.update({
        'Authorization': f'Bearer {token}'
    })
```

### API Key Authentication

```python
def setup_api_key_auth(self, api_key: str, header_name: str = 'X-API-Key'):
    """Setup API key authentication"""
    self.session.headers.update({
        header_name: api_key
    })
```

### OAuth 2.0 Authentication

```python
def setup_oauth_auth(self, client_id: str, client_secret: str, token_url: str):
    """Setup OAuth 2.0 authentication"""
    # Get access token
    token_response = requests.post(token_url, data={
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    })
    
    if token_response.status_code == 200:
        token_data = token_response.json()
        access_token = token_data['access_token']
        
        self.session.headers.update({
            'Authorization': f'Bearer {access_token}'
        })
    else:
        raise Exception('Failed to obtain OAuth token')
```

## Data Mapping

### API-Specific Field Mapping

Different APIs may expect different field names:

```json
{
  "api_mappings": {
    "salesforce": {
      "name": "Company",
      "email": "Email",
      "phone": "Phone"
    },
    "hubspot": {
      "name": "company",
      "email": "email",
      "phone": "phone"
    }
  }
}
```

### Dynamic Field Mapping

```python
def map_fields_for_api(self, customer_data: dict, api_type: str) -> dict:
    """Map fields based on API requirements"""
    mapping = self.get_api_mapping(api_type)
    
    mapped_data = {}
    for internal_field, api_field in mapping.items():
        if internal_field in customer_data:
            mapped_data[api_field] = customer_data[internal_field]
    
    return mapped_data
```

## Testing API Integration

### Unit Tests

```python
import pytest
from unittest.mock import Mock, patch
from scripts.customer_api_client import CustomerAPIClient

def test_successful_customer_creation():
    client = CustomerAPIClient("https://api.test.com", "test-key")
    
    with patch.object(client.session, 'post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "123", "status": "created"}
        mock_post.return_value = mock_response
        
        success, response = client.create_customer({"name": "Test Corp"})
        
        assert success == True
        assert response["id"] == "123"

def test_api_error_handling():
    client = CustomerAPIClient("https://api.test.com", "test-key")
    
    with patch.object(client.session, 'post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        success, response = client.create_customer({"name": "Test Corp"})
        
        assert success == False
        assert response["status_code"] == 400
```

### Integration Tests

```python
def test_real_api_integration():
    """Test with actual API (use with caution)"""
    client = CustomerAPIClient("https://jsonplaceholder.typicode.com")
    
    test_customer = {
        "name": "Test Company",
        "email": "test@example.com"
    }
    
    success, response = client.create_customer(test_customer)
    assert success == True
```

## Monitoring and Logging

### API Performance Monitoring

```python
def monitor_api_performance(self, start_time: float, end_time: float, 
                          success: bool, endpoint: str):
    """Monitor API performance metrics"""
    response_time = end_time - start_time
    
    # Log performance metrics
    logger.info(f"API Call - Endpoint: {endpoint}, "
                f"Response Time: {response_time:.2f}s, "
                f"Success: {success}")
    
    # Send to monitoring system
    if hasattr(self, 'metrics_client'):
        self.metrics_client.gauge('api.response_time', response_time, 
                                 tags=[f'endpoint:{endpoint}'])
        self.metrics_client.increment('api.calls', 
                                     tags=[f'endpoint:{endpoint}', f'success:{success}'])
```

### Error Logging

```python
def log_api_error(self, error_details: dict, customer_data: dict):
    """Log API errors for debugging"""
    logger.error(f"API Error: {error_details}")
    
    # Sanitize customer data for logging
    safe_customer_data = {
        'name': customer_data.get('name', 'N/A'),
        'email': customer_data.get('email', 'N/A')[:5] + '***' if customer_data.get('email') else 'N/A'
    }
    
    logger.error(f"Customer Data: {safe_customer_data}")
```

## Best Practices

### 1. Security
- Never log sensitive data (API keys, full email addresses)
- Use environment variables for credentials
- Implement proper error message sanitization

### 2. Performance
- Use connection pooling
- Implement proper timeout settings
- Use batch processing for multiple records

### 3. Reliability
- Implement retry logic with exponential backoff
- Handle network errors gracefully
- Validate API responses

### 4. Monitoring
- Log all API interactions
- Monitor response times and error rates
- Set up alerts for API failures

### 5. Testing
- Test with mock APIs first
- Implement comprehensive error scenarios
- Use integration tests sparingly

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Verify API credentials
   - Check token expiration
   - Confirm authentication method

2. **Rate Limiting**
   - Reduce batch size
   - Increase delays between requests
   - Implement exponential backoff

3. **Network Issues**
   - Check connectivity
   - Verify SSL certificates
   - Test with curl/Postman first

4. **Data Format Issues**
   - Verify field mappings
   - Check data types
   - Validate JSON structure

### Debug Tools

Use these tools to debug API issues:

```bash
# Test API endpoint with curl
curl -X POST https://api.example.com/customers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"name": "Test Company", "email": "test@example.com"}'

# Monitor network traffic
tcpdump -i any -s 0 -w api_traffic.pcap host api.example.com

# Test SSL certificate
openssl s_client -connect api.example.com:443
```



