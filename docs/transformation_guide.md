# Data Transformation Guide

This guide explains how to customize data transformations in the CSV Upload System to meet your specific business requirements.

## Overview

The transformation system is designed to be easily configurable through JSON configuration files, allowing you to modify data processing rules without changing code.

## Configuration Structure

The main configuration file is located at `config/transformation_rules.json` and contains several sections:

```json
{
  "field_mappings": {},
  "validations": {},
  "transformations": {},
  "required_fields": [],
  "api_config": {},
  "processing_config": {}
}
```

## Field Mappings

Field mappings define how CSV column names are mapped to the target customer object structure.

### Basic Field Mapping
```json
{
  "field_mappings": {
    "company_name": "name",
    "contact_email": "email",
    "contact_first_name": "firstName",
    "contact_last_name": "lastName"
  }
}
```

### Advanced Field Mapping Examples

#### Handling Multiple Source Fields
```json
{
  "field_mappings": {
    "first_name": "firstName",
    "fname": "firstName",
    "given_name": "firstName",
    "last_name": "lastName",
    "surname": "lastName",
    "family_name": "lastName"
  }
}
```

#### Nested Object Mapping
```json
{
  "field_mappings": {
    "billing_street": "address.street",
    "billing_city": "address.city",
    "billing_state": "address.state",
    "billing_zip": "address.postalCode"
  }
}
```

## Transformations

Transformations apply data processing rules to clean and format data.

### Available Transformation Types

#### String Transformations
```json
{
  "transformations": {
    "name": "title_case",        // "john doe" -> "John Doe"
    "email": "lowercase",        // "JOHN@EXAMPLE.COM" -> "john@example.com"
    "code": "uppercase",         // "abc123" -> "ABC123"
    "address": "clean_string"    // Remove extra whitespace
  }
}
```

#### Phone Number Normalization
```json
{
  "transformations": {
    "phone": "normalize_phone"   // "555-123-4567" -> "+1-555-123-4567"
  }
}
```

### Custom Transformations

You can add custom transformations by extending the `DataTransformer` class:

```python
def custom_date_format(self, date_str: str) -> str:
    """Convert date to ISO format"""
    if not date_str:
        return date_str
    
    # Handle various date formats
    formats = ['%m/%d/%Y', '%d-%m-%Y', '%Y-%m-%d']
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date.isoformat()
        except ValueError:
            continue
    
    return date_str

def custom_currency_format(self, amount: str) -> str:
    """Format currency values"""
    if not amount:
        return amount
    
    # Remove currency symbols and format
    cleaned = re.sub(r'[^\d.,]', '', amount)
    # Add your currency formatting logic here
    return cleaned
```

Then add to your transformations:
```json
{
  "transformations": {
    "date_created": "custom_date_format",
    "revenue": "custom_currency_format"
  }
}
```

## Validations

Validations ensure data quality and business rule compliance.

### Built-in Validations

#### Email Validation
```json
{
  "validations": {
    "email": "email_format"
  }
}
```

#### Phone Validation
```json
{
  "validations": {
    "phone": "phone_format"
  }
}
```

#### Required Field Validation
```json
{
  "validations": {
    "name": "required",
    "email": "required"
  }
}
```

### Custom Validations

Add custom validation rules:

```python
def validate_company_size(self, size: str) -> tuple[bool, str]:
    """Validate company size format"""
    if not size:
        return True, ""
    
    # Check if size matches expected format (e.g., "50-100")
    if not re.match(r'^\d+-\d+$', size):
        return False, f"Invalid company size format: {size}"
    
    # Check if range is valid
    try:
        min_size, max_size = map(int, size.split('-'))
        if min_size >= max_size:
            return False, f"Invalid size range: {size}"
    except ValueError:
        return False, f"Invalid size format: {size}"
    
    return True, ""

def validate_tax_id(self, tax_id: str) -> tuple[bool, str]:
    """Validate tax ID format"""
    if not tax_id:
        return True, ""
    
    # Remove common prefixes
    cleaned_id = re.sub(r'^TAX-?', '', tax_id.upper())
    
    # Check format (alphanumeric, specific length)
    if not re.match(r'^[A-Z0-9]{6,12}$', cleaned_id):
        return False, f"Invalid tax ID format: {tax_id}"
    
    return True, ""
```

Add to validations:
```json
{
  "validations": {
    "company_size": "validate_company_size",
    "tax_id": "validate_tax_id"
  }
}
```

## Complex Transformation Scenarios

### Conditional Transformations

```python
def conditional_phone_format(self, phone: str, country: str) -> str:
    """Format phone based on country"""
    if not phone:
        return phone
    
    if country.upper() == 'USA':
        return self.normalize_phone(phone)
    elif country.upper() == 'UK':
        return self.format_uk_phone(phone)
    else:
        return phone
```

### Data Enrichment

```python
def enrich_customer_data(self, customer: dict) -> dict:
    """Add computed fields"""
    # Add full name
    if customer.get('firstName') and customer.get('lastName'):
        customer['fullName'] = f"{customer['firstName']} {customer['lastName']}"
    
    # Add company domain
    if customer.get('email'):
        domain = customer['email'].split('@')[1] if '@' in customer['email'] else ''
        customer['companyDomain'] = domain
    
    # Add region based on country
    country = customer.get('address', {}).get('country', '').upper()
    region_mapping = {
        'USA': 'North America',
        'CANADA': 'North America',
        'UK': 'Europe',
        'GERMANY': 'Europe'
    }
    customer['region'] = region_mapping.get(country, 'Unknown')
    
    return customer
```

## Error Handling in Transformations

### Graceful Error Handling

```python
def safe_transformation(self, value: str, transformation_func: str) -> str:
    """Apply transformation with error handling"""
    try:
        return self.transform_field("temp", value, transformation_func)
    except Exception as e:
        logger.warning(f"Transformation failed for value '{value}': {e}")
        return value  # Return original value on failure
```

### Error Collection

```python
def transform_with_errors(self, row_data: dict, row_number: int) -> tuple[dict, list]:
    """Transform row and collect all errors"""
    transformed_data = {}
    errors = []
    
    for field, value in row_data.items():
        try:
            # Apply transformation
            transformed_value = self.transform_field(field, value, "title_case")
            transformed_data[field] = transformed_value
        except Exception as e:
            errors.append({
                'type': 'transformation_error',
                'row_number': row_number,
                'field': field,
                'value': value,
                'message': str(e)
            })
            transformed_data[field] = value  # Keep original value
    
    return transformed_data, errors
```

## Testing Transformations

### Unit Testing

```python
import pytest
from scripts.data_transformer import DataTransformer

def test_title_case_transformation():
    transformer = DataTransformer()
    result = transformer.title_case("john doe")
    assert result == "John Doe"

def test_phone_normalization():
    transformer = DataTransformer()
    result = transformer.normalize_phone("555-123-4567")
    assert result == "+1-555-123-4567"

def test_email_validation():
    transformer = DataTransformer()
    assert transformer.validate_email("test@example.com") == True
    assert transformer.validate_email("invalid-email") == False
```

### Integration Testing

```python
def test_full_transformation():
    config = {
        "field_mappings": {"company_name": "name"},
        "transformations": {"name": "title_case"},
        "validations": {"name": "required"}
    }
    
    transformer = DataTransformer(config)
    test_data = [{"company_name": "acme corp", "contact_email": "test@acme.com"}]
    
    transformed_data, errors = transformer.transform_batch(test_data)
    
    assert len(transformed_data) == 1
    assert transformed_data[0]["name"] == "Acme Corp"
    assert len(errors) == 0
```

## Performance Optimization

### Batch Processing

```python
def process_large_dataset(self, data: list, batch_size: int = 1000) -> list:
    """Process large datasets in batches"""
    results = []
    
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        transformed_batch, errors = self.transform_batch(batch)
        results.extend(transformed_batch)
    
    return results
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_transformation(self, value: str, transformation_type: str) -> str:
    """Cache transformation results for repeated values"""
    return self.transform_field("temp", value, transformation_type)
```

## Best Practices

### 1. Configuration Management
- Keep transformation rules in version control
- Use environment-specific configurations
- Document all custom transformations

### 2. Error Handling
- Always handle transformation failures gracefully
- Provide meaningful error messages
- Log transformation errors for debugging

### 3. Performance
- Test transformations with large datasets
- Use batch processing for efficiency
- Cache frequently used transformations

### 4. Maintainability
- Keep transformations simple and focused
- Use descriptive names for custom functions
- Write comprehensive tests

### 5. Data Quality
- Validate input data before transformation
- Preserve original data when possible
- Implement data quality metrics

## Troubleshooting

### Common Issues

1. **Transformation Not Applied**
   - Check field mapping configuration
   - Verify transformation function exists
   - Check for typos in configuration

2. **Validation Failures**
   - Review validation rules
   - Check input data format
   - Test validation functions independently

3. **Performance Issues**
   - Profile transformation functions
   - Use batch processing
   - Consider caching strategies

4. **Data Loss**
   - Check for empty value handling
   - Verify transformation logic
   - Test with edge cases

### Debug Mode

Enable debug logging to troubleshoot transformations:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_transformation(self, field: str, value: str, result: str):
    logger.debug(f"Transformed {field}: '{value}' -> '{result}'")
```



