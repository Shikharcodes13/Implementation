import csv
import io
import chardet
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class CSVParser:
    def __init__(self):
        self.supported_encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
        self.supported_delimiters = [',', ';', '\t', '|']

    def _resolve_delimiter(self, provided_delimiter: str, text_content: str) -> str:
        """Resolve delimiter to a safe 1-character string.
        If invalid or not provided, attempt to sniff; fallback to ','."""
        try:
            if isinstance(provided_delimiter, str) and len(provided_delimiter) == 1:
                return provided_delimiter
        except Exception:
            pass
        # Try to sniff from sample of the content
        sample = text_content[:8192]
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=''.join(self.supported_delimiters))
            if dialect.delimiter in self.supported_delimiters:
                return dialect.delimiter
        except Exception:
            pass
        return ','
    
    def detect_encoding(self, file_content: bytes) -> str:
        """Detect file encoding"""
        result = chardet.detect(file_content)
        detected_encoding = result['encoding']
        
        if detected_encoding in self.supported_encodings:
            return detected_encoding
        
        # Fallback to utf-8
        return 'utf-8'
    
    def parse_csv(self, file_content: bytes, delimiter: str = ',') -> Tuple[List[Dict[str, Any]], List[str], List[Dict]]:
        """
        Parse CSV file and return data, headers, and errors
        
        Returns:
            - parsed_data: List of dictionaries with row data
            - headers: List of column headers
            - errors: List of parsing errors
        """
        errors = []
        parsed_data = []
        headers = []
        
        try:
            # Detect encoding
            encoding = self.detect_encoding(file_content)
            
            # Decode content
            try:
                text_content = file_content.decode(encoding)
            except UnicodeDecodeError:
                # Try with utf-8 and replace errors
                text_content = file_content.decode('utf-8', errors='replace')
                errors.append({
                    'type': 'encoding_warning',
                    'message': f'Encoding issues detected, some characters may be replaced'
                })
            
            # Resolve delimiter safely
            safe_delimiter = self._resolve_delimiter(delimiter, text_content)
            if not isinstance(delimiter, str) or len(delimiter) != 1 or delimiter != safe_delimiter:
                errors.append({
                    'type': 'delimiter_warning',
                    'message': f"Provided delimiter was invalid; using '{safe_delimiter}' instead"
                })

            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(text_content), delimiter=safe_delimiter)
            headers = csv_reader.fieldnames or []
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (header is 1)
                try:
                    # Clean empty values
                    cleaned_row = {k: v.strip() if v else '' for k, v in row.items()}
                    parsed_data.append(cleaned_row)
                except Exception as e:
                    errors.append({
                        'type': 'row_parsing_error',
                        'row_number': row_num,
                        'message': f'Error parsing row: {str(e)}',
                        'raw_data': row
                    })
        
        except Exception as e:
            errors.append({
                'type': 'file_parsing_error',
                'message': f'Failed to parse CSV file: {str(e)}'
            })
        
        return parsed_data, headers, errors
    
    def validate_csv_structure(self, data: List[Dict], required_fields: List[str]) -> List[Dict]:
        """Validate CSV structure and required fields"""
        errors = []
        
        if not data:
            errors.append({
                'type': 'empty_file',
                'message': 'CSV file is empty or contains no data rows'
            })
            return errors
        
        # Check if all required fields are present
        first_row = data[0]
        missing_fields = [field for field in required_fields if field not in first_row]
        
        if missing_fields:
            errors.append({
                'type': 'missing_required_fields',
                'message': f'Missing required fields: {", ".join(missing_fields)}',
                'missing_fields': missing_fields
            })
        
        # Check for completely empty rows
        for i, row in enumerate(data, start=2):
            if not any(row.values()):
                errors.append({
                    'type': 'empty_row',
                    'row_number': i,
                    'message': 'Row is completely empty'
                })
        
        return errors

def main(file_content: bytes, delimiter: str = ',', required_fields: List[str] = None) -> Dict[str, Any]:
    """
    Main function for Windmill integration
    
    Args:
        file_content: CSV file content as bytes
        delimiter: CSV delimiter (default: ',')
        required_fields: List of required field names
    
    Returns:
        Dictionary with parsed data, headers, and errors
    """
    if required_fields is None:
        required_fields = [
            'company_name', 'contact_email', 'contact_first_name', 
            'contact_last_name', 'phone_number'
        ]
    
    parser = CSVParser()
    parsed_data, headers, parsing_errors = parser.parse_csv(file_content, delimiter)
    validation_errors = parser.validate_csv_structure(parsed_data, required_fields)
    
    all_errors = parsing_errors + validation_errors
    
    return {
        'data': parsed_data,
        'headers': headers,
        'errors': all_errors,
        'total_rows': len(parsed_data),
        'valid_rows': len(parsed_data) - len([e for e in all_errors if 'row_number' in e])
    }

