import re
import json
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataTransformer:
    def __init__(self, transformation_rules: Dict[str, Any] = None):
        self.transformation_rules = transformation_rules or {}
        self.field_mappings = self.transformation_rules.get('field_mappings', {})
        self.validations = self.transformation_rules.get('validations', {})
        self.transformations = self.transformation_rules.get('transformations', {})
    
    def validate_email(self, email: str) -> bool:
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_phone(self, phone: str) -> bool:
        if not phone:
            return False
        digits_only = re.sub(r'\D', '', phone)
        return len(digits_only) >= 10
    
    def normalize_phone(self, phone: str) -> str:
        if not phone:
            return phone
        digits_only = re.sub(r'\D', '', phone)
        if len(digits_only) == 10:
            return f"+1-{digits_only[:3]}-{digits_only[3:6]}-{digits_only[6:]}"
        elif len(digits_only) == 11 and digits_only[0] == '1':
            return f"+1-{digits_only[1:4]}-{digits_only[4:7]}-{digits_only[7:]}"
        return phone
    
    def title_case(self, text: str) -> str:
        return text.title() if text else text
    
    def clean_string(self, text: str) -> str:
        return re.sub(r'\s+', ' ', text.strip()) if text else ""
    
    def transform_field(self, field_name: str, value: str, transformation_type: str) -> str:
        if not value:
            return value
        if transformation_type == 'title_case':
            return self.title_case(value)
        elif transformation_type == 'normalize_phone':
            return self.normalize_phone(value)
        elif transformation_type == 'clean_string':
            return self.clean_string(value)
        elif transformation_type == 'lowercase':
            return value.lower()
        elif transformation_type == 'uppercase':
            return value.upper()
        return value
    
    def validate_field(self, field_name: str, value: str, validation_type: str) -> tuple[bool, str]:
        if not value:
            return True, ""
        if validation_type == 'email_format' and not self.validate_email(value):
            return False, f"Invalid email format: {value}"
        elif validation_type == 'phone_format' and not self.validate_phone(value):
            return False, f"Invalid phone format: {value}"
        elif validation_type == 'required' and not value.strip():
            return False, f"Required field is empty: {field_name}"
        return True, ""
    
    def map_field_name(self, original_name: str) -> str:
        return self.field_mappings.get(original_name, original_name)
    
    def transform_row(self, row_data: Dict[str, Any], row_number: int) -> tuple[Dict[str, Any], List[Dict]]:
        errors = []
        transformed_data = {}
        
        for original_field, value in row_data.items():
            if not value:
                continue
            target_field = self.map_field_name(original_field)
            transformed_value = value
            if target_field in self.transformations:
                transformed_value = self.transform_field(
                    target_field, value, self.transformations[target_field]
                )
            if target_field in self.validations:
                is_valid, error_message = self.validate_field(
                    target_field, transformed_value, self.validations[target_field]
                )
                if not is_valid:
                    errors.append({
                        'type': 'validation_error',
                        'row_number': row_number,
                        'field': target_field,
                        'value': transformed_value,
                        'message': error_message
                    })
            transformed_data[target_field] = transformed_value
        
        customer_object = self.build_customer_object(transformed_data)
        return customer_object, errors
    
    def build_customer_object(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'name': data.get('name', ''),
            'email': data.get('email', ''),
            'firstName': data.get('firstName', ''),
            'lastName': data.get('lastName', ''),
            'phone': data.get('phone', ''),
            'address': {
                'street': data.get('address', ''),
                'city': data.get('city', ''),
                'country': data.get('country', ''),
                'postalCode': data.get('postalCode', '')
            },
            'metadata': {
                'taxId': data.get('taxId', ''),
                'companySize': data.get('companySize', ''),
                'importDate': datetime.now().isoformat(),
                'source': 'csv_upload'
            }
        }
    
    def transform_batch(self, data: List[Dict[str, Any]]) -> tuple[List[Dict], List[Dict]]:
        transformed_data = []
        all_errors = []
        for i, row in enumerate(data, start=1):
            try:
                customer_obj, errors = self.transform_row(row, i)
                transformed_data.append(customer_obj)
                all_errors.extend(errors)
            except Exception as e:
                all_errors.append({
                    'type': 'transformation_error',
                    'row_number': i,
                    'message': f'Failed to transform row: {str(e)}',
                    'raw_data': row
                })
        return transformed_data, all_errors


def main(input_data: Any, transformation_rules: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Main function for Windmill integration.
    Accepts either the full parser output (with 'data', 'errors', etc.)
    or just a list of row dicts.
    """
    # Ensure input is always iterable
    if isinstance(input_data, dict) and "data" in input_data:
        rows = input_data.get("data") or []
    else:
        rows = input_data or []

    if not rows:
        logger.warning("No input rows found. Nothing to transform.")

    transformer = DataTransformer(transformation_rules)
    transformed_data, errors = transformer.transform_batch(rows)

    return {
        'transformed_data': transformed_data,
        'errors': errors,
        'total_rows': len(rows),
        'successful_transformations': len(transformed_data),
        'failed_transformations': len(errors)
    }
