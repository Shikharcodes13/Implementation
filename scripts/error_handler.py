from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ErrorHandler:
    def __init__(self):
        self.error_types = {
            'parsing_error': 'CSV Parsing Error',
            'validation_error': 'Data Validation Error',
            'transformation_error': 'Data Transformation Error',
            'api_error': 'API Integration Error',
            'connection_error': 'Connection Error',
            'timeout_error': 'Timeout Error',
            'empty_file': 'Empty File Error',
            'missing_required_fields': 'Missing Required Fields',
            'empty_row': 'Empty Row Error'
        }
    
    def categorize_errors(self, errors: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Categorize errors by type"""
        categorized = {}
        
        for error in errors:
            error_type = error.get('type', 'unknown')
            
            if error_type not in categorized:
                categorized[error_type] = []
            
            categorized[error_type].append(error)
        
        return categorized
    
    def get_error_summary(self, errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate error summary statistics"""
        if not errors:
            return {
                'total_errors': 0,
                'error_types': {},
                'rows_with_errors': set(),
                'critical_errors': 0,
                'warning_errors': 0
            }
        
        categorized = self.categorize_errors(errors)
        
        # Count errors by type
        error_counts = {}
        rows_with_errors = set()
        critical_errors = 0
        warning_errors = 0
        
        for error_type, error_list in categorized.items():
            error_counts[error_type] = len(error_list)
            
            for error in error_list:
                if 'row_number' in error:
                    rows_with_errors.add(error['row_number'])
                
                # Categorize severity
                if error_type in ['parsing_error', 'missing_required_fields', 'api_error']:
                    critical_errors += 1
                else:
                    warning_errors += 1
        
        return {
            'total_errors': len(errors),
            'error_types': error_counts,
            'rows_with_errors': list(rows_with_errors),
            'critical_errors': critical_errors,
            'warning_errors': warning_errors
        }
    
    def get_failed_rows(self, errors: List[Dict[str, Any]], original_data: List[Dict]) -> List[Dict]:
        """Get original data for rows that failed processing"""
        failed_rows = []
        failed_row_numbers = set()
        
        # Collect row numbers that failed
        for error in errors:
            if 'row_number' in error:
                failed_row_numbers.add(error['row_number'])
        
        # Get original data for failed rows
        for row_num in failed_row_numbers:
            if 1 <= row_num <= len(original_data):
                failed_rows.append({
                    'row_number': row_num,
                    'data': original_data[row_num - 1],
                    'errors': [e for e in errors if e.get('row_number') == row_num]
                })
        
        return failed_rows
    
    def format_error_message(self, error: Dict[str, Any]) -> str:
        """Format error message for display"""
        error_type = error.get('type', 'unknown')
        message = error.get('message', 'Unknown error')
        
        if 'row_number' in error:
            return f"Row {error['row_number']}: {message}"
        else:
            return message
    
    def create_error_report(self, errors: List[Dict[str, Any]], 
                          original_data: List[Dict] = None) -> Dict[str, Any]:
        """Create comprehensive error report"""
        summary = self.get_error_summary(errors)
        categorized = self.categorize_errors(errors)
        failed_rows = self.get_failed_rows(errors, original_data) if original_data else []
        
        # Create detailed error list
        detailed_errors = []
        for error_type, error_list in categorized.items():
            for error in error_list:
                detailed_errors.append({
                    'type': error_type,
                    'type_label': self.error_types.get(error_type, error_type),
                    'message': self.format_error_message(error),
                    'details': error,
                    'timestamp': datetime.now().isoformat()
                })
        
        return {
            'summary': summary,
            'detailed_errors': detailed_errors,
            'failed_rows': failed_rows,
            'generated_at': datetime.now().isoformat(),
            'total_rows_processed': len(original_data) if original_data else 0
        }

def main(errors: List[Dict[str, Any]], original_data: List[Dict] = None) -> Dict[str, Any]:
    """
    Main function for Windmill integration
    
    Args:
        errors: List of errors from processing
        original_data: Original CSV data for reference
    
    Returns:
        Comprehensive error report
    """
    handler = ErrorHandler()
    return handler.create_error_report(errors, original_data)



