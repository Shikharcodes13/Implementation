import hashlib
import json
import random
from datetime import datetime
from typing import Dict, Any

def main(customer_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mock Customer API endpoint for testing
    
    This script simulates a real customer API with:
    - Customer creation with unique IDs
    - Validation of required fields
    - Random error simulation for testing
    - Proper response formatting
    
    Args:
        customer_data: Customer data dictionary
        
    Returns:
        API response dictionary
    """
    
    # Simulate random API failures (5% failure rate)
    if random.random() < 0.05:
        return {
            "success": False,
            "error": "api_error",
            "message": "Simulated API server error",
            "status_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    
    # Validate required fields
    required_fields = ['name', 'email']
    missing_fields = [field for field in required_fields if not customer_data.get(field)]
    
    if missing_fields:
        return {
            "success": False,
            "error": "validation_error",
            "message": f"Missing required fields: {', '.join(missing_fields)}",
            "status_code": 400,
            "missing_fields": missing_fields,
            "timestamp": datetime.now().isoformat()
        }
    
    # Simulate email format validation
    email = customer_data.get('email', '')
    if email and '@' not in email:
        return {
            "success": False,
            "error": "validation_error",
            "message": "Invalid email format",
            "status_code": 400,
            "field": "email",
            "value": email,
            "timestamp": datetime.now().isoformat()
        }
    
    # Generate unique customer ID based on data
    customer_json = json.dumps(customer_data, sort_keys=True)
    customer_id = hashlib.md5(customer_json.encode()).hexdigest()[:8]
    
    # Simulate processing delay
    import time
    time.sleep(random.uniform(0.1, 0.5))
    
    # Create successful response
    response = {
        "success": True,
        "customer": {
            "id": f"cust_{customer_id}",
            "external_id": customer_id,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            **customer_data
        },
        "api_version": "1.0",
        "processing_time_ms": random.randint(50, 200),
        "timestamp": datetime.now().isoformat()
    }
    
    return response

def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for API monitoring
    
    Returns:
        Health status dictionary
    """
    return {
        "status": "healthy",
        "service": "Mock Customer API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime": "100%",
        "database": "connected",
        "external_services": "available"
    }



