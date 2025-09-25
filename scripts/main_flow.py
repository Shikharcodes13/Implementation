import time
import json
from typing import Dict, Any, List
from datetime import datetime

def main(file_content: bytes, 
         delimiter: str = ',', 
         api_base_url: str = 'https://jsonplaceholder.typicode.com',
         api_key: str = None,
         batch_size: int = 10) -> Dict[str, Any]:
    """
    Main orchestration script for CSV upload and processing
    
    This script coordinates the entire CSV processing pipeline:
    1. Parse CSV file
    2. Transform data according to rules
    3. Create customers via API
    4. Handle errors and generate reports
    
    Args:
        file_content: Raw CSV file content as bytes
        delimiter: CSV delimiter character
        api_base_url: Base URL for customer API
        api_key: API authentication key
        batch_size: Number of customers to process per batch
        
    Returns:
        Complete processing results with reports
    """
    
    start_time = time.time()
    
    # Load transformation rules
    transformation_rules = {
        "field_mappings": {
            "company_name": "name",
            "contact_email": "email",
            "contact_first_name": "firstName",
            "contact_last_name": "lastName",
            "phone_number": "phone",
            "address": "address",
            "city": "city",
            "country": "country",
            "postal_code": "postalCode",
            "tax_id": "taxId",
            "company_size": "companySize"
        },
        "validations": {
            "email": "email_format",
            "phone": "phone_format",
            "name": "required",
            "firstName": "required",
            "lastName": "required"
        },
        "transformations": {
            "name": "title_case",
            "firstName": "title_case",
            "lastName": "title_case",
            "phone": "normalize_phone",
            "email": "lowercase",
            "address": "clean_string",
            "city": "title_case"
        }
    }
    
    required_fields = [
        'company_name', 'contact_email', 'contact_first_name', 'contact_last_name'
    ]
    
    all_errors = []
    
    try:
        # Step 1: Parse CSV
        from scripts.csv_parser import CSVParser
        parser = CSVParser()
        parsed_data, headers, parsing_errors = parser.parse_csv(file_content, delimiter)
        validation_errors = parser.validate_csv_structure(parsed_data, required_fields)
        
        all_errors.extend(parsing_errors)
        all_errors.extend(validation_errors)
        
        if not parsed_data:
            return {
                'success': False,
                'error': 'No valid data to process',
                'errors': all_errors,
                'processing_time': time.time() - start_time
            }
        
        # Step 2: Transform data
        from scripts.data_transformer import DataTransformer
        transformer = DataTransformer(transformation_rules)
        transformed_data, transformation_errors = transformer.transform_batch(parsed_data)
        
        all_errors.extend(transformation_errors)
        
        # Step 3: Create customers via API
        api_results = {'results': {'total_processed': 0, 'total_successful': 0, 'total_failed': 0, 'successful': [], 'failed': []}}
        
        if transformed_data:
            from scripts.customer_api_client import CustomerAPIClient
            client = CustomerAPIClient(api_base_url, api_key)
            api_results = client.create_customers_batch(transformed_data, batch_size)
            
            # Add API errors to all_errors
            for failed_call in api_results.get('results', {}).get('failed', []):
                error_details = failed_call.get('error_details', {})
                all_errors.append({
                    'type': 'api_error',
                    'message': error_details.get('message', 'API call failed'),
                    'customer_email': failed_call.get('customer_data', {}).get('email', 'Unknown'),
                    'error_details': error_details
                })
        
        # Step 4: Generate error report
        from scripts.error_handler import ErrorHandler
        error_handler = ErrorHandler()
        error_report = error_handler.create_error_report(all_errors, parsed_data)
        
        # Step 5: Generate processing report
        processing_time = time.time() - start_time
        
        from scripts.report_generator import ReportGenerator
        report_generator = ReportGenerator()
        
        processing_summary = {
            'total_rows': len(parsed_data),
            'successful_rows': len(transformed_data) - len(transformation_errors),
            'failed_rows': len(transformation_errors)
        }
        
        complete_report = report_generator.generate_complete_report(
            processing_summary=processing_summary,
            data_quality={'transformed_data': transformed_data},
            api_results=api_results,
            errors=all_errors,
            transformed_data=transformed_data,
            processing_time=processing_time
        )
        
        # Calculate success metrics
        total_rows = len(parsed_data)
        successful_api_calls = api_results.get('results', {}).get('total_successful', 0)
        failed_api_calls = api_results.get('results', {}).get('total_failed', 0)
        
        return {
            'success': True,
            'summary': {
                'total_rows_processed': total_rows,
                'successful_transformations': len(transformed_data),
                'successful_api_calls': successful_api_calls,
                'failed_api_calls': failed_api_calls,
                'total_errors': len(all_errors),
                'processing_time_seconds': round(processing_time, 2),
                'success_rate': round((successful_api_calls / total_rows * 100) if total_rows > 0 else 0, 2)
            },
            'data': {
                'parsed_data': parsed_data[:10],  # First 10 rows for preview
                'transformed_data': transformed_data[:10],  # First 10 transformed rows
                'headers': headers
            },
            'api_results': api_results,
            'error_report': error_report,
            'complete_report': complete_report,
            'processing_time': processing_time
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Processing failed: {str(e)}',
            'errors': all_errors,
            'processing_time': time.time() - start_time
        }



