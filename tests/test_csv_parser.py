import pytest
import io
from scripts.csv_parser import CSVParser

class TestCSVParser:
    def setup_method(self):
        self.parser = CSVParser()
    
    def test_parse_valid_csv(self):
        """Test parsing a valid CSV file"""
        csv_content = b"name,email,phone\nJohn Doe,john@example.com,555-1234\nJane Smith,jane@example.com,555-5678"
        
        data, headers, errors = self.parser.parse_csv(csv_content)
        
        assert len(data) == 2
        assert headers == ['name', 'email', 'phone']
        assert len(errors) == 0
        assert data[0]['name'] == 'John Doe'
        assert data[1]['email'] == 'jane@example.com'
    
    def test_parse_csv_with_encoding_issues(self):
        """Test parsing CSV with encoding issues"""
        # Create CSV with special characters
        csv_content = "name,email\nJohn Döe,john@example.com".encode('latin-1')
        
        data, headers, errors = self.parser.parse_csv(csv_content)
        
        assert len(data) == 1
        assert len(errors) <= 1  # May have encoding warning
    
    def test_validate_csv_structure_missing_fields(self):
        """Test validation with missing required fields"""
        data = [{'name': 'John', 'email': 'john@example.com'}]
        required_fields = ['name', 'email', 'phone']
        
        errors = self.parser.validate_csv_structure(data, required_fields)
        
        assert len(errors) == 1
        assert errors[0]['type'] == 'missing_required_fields'
        assert 'phone' in errors[0]['missing_fields']
    
    def test_validate_empty_csv(self):
        """Test validation of empty CSV"""
        data = []
        required_fields = ['name', 'email']
        
        errors = self.parser.validate_csv_structure(data, required_fields)
        
        assert len(errors) == 1
        assert errors[0]['type'] == 'empty_file'
    
    def test_parse_csv_with_different_delimiter(self):
        """Test parsing CSV with semicolon delimiter"""
        csv_content = b"name;email;phone\nJohn Doe;john@example.com;555-1234"
        
        data, headers, errors = self.parser.parse_csv(csv_content, delimiter=';')
        
        assert len(data) == 1
        assert headers == ['name', 'email', 'phone']
        assert data[0]['name'] == 'John Doe'
    
    def test_main_function(self):
        """Test the main function for Windmill integration"""
        from scripts.csv_parser import main
        
        csv_content = b"company_name,contact_email,contact_first_name,contact_last_name,phone_number\nAcme Corp,john@acme.com,John,Doe,555-1234"
        
        result = main(csv_content)
        
        assert 'data' in result
        assert 'headers' in result
        assert 'errors' in result
        assert result['total_rows'] == 1
        assert len(result['data']) == 1



