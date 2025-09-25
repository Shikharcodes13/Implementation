import pytest
from scripts.data_transformer import DataTransformer

class TestDataTransformer:
    def setup_method(self):
        self.transformation_rules = {
            "field_mappings": {
                "company_name": "name",
                "contact_email": "email",
                "contact_first_name": "firstName",
                "contact_last_name": "lastName"
            },
            "validations": {
                "email": "email_format",
                "name": "required"
            },
            "transformations": {
                "name": "title_case",
                "email": "lowercase"
            }
        }
        self.transformer = DataTransformer(self.transformation_rules)
    
    def test_email_validation(self):
        """Test email validation"""
        assert self.transformer.validate_email("test@example.com") == True
        assert self.transformer.validate_email("invalid-email") == False
        assert self.transformer.validate_email("") == False
    
    def test_phone_validation(self):
        """Test phone validation"""
        assert self.transformer.validate_phone("555-123-4567") == True
        assert self.transformer.validate_phone("5551234567") == True
        assert self.transformer.validate_phone("123") == False
        assert self.transformer.validate_phone("") == False
    
    def test_phone_normalization(self):
        """Test phone number normalization"""
        assert self.transformer.normalize_phone("555-123-4567") == "+1-555-123-4567"
        assert self.transformer.normalize_phone("5551234567") == "+1-555-123-4567"
        assert self.transformer.normalize_phone("15551234567") == "+1-555-123-4567"
        assert self.transformer.normalize_phone("") == ""
    
    def test_title_case(self):
        """Test title case transformation"""
        assert self.transformer.title_case("john doe") == "John Doe"
        assert self.transformer.title_case("ACME CORP") == "Acme Corp"
        assert self.transformer.title_case("") == ""
    
    def test_field_mapping(self):
        """Test field name mapping"""
        assert self.transformer.map_field_name("company_name") == "name"
        assert self.transformer.map_field_name("contact_email") == "email"
        assert self.transformer.map_field_name("unknown_field") == "unknown_field"
    
    def test_transform_row(self):
        """Test single row transformation"""
        row_data = {
            "company_name": "acme corp",
            "contact_email": "JOHN@ACME.COM",
            "contact_first_name": "john",
            "contact_last_name": "doe"
        }
        
        customer_obj, errors = self.transformer.transform_row(row_data, 1)
        
        assert customer_obj['name'] == "Acme Corp"
        assert customer_obj['email'] == "john@acme.com"
        assert customer_obj['firstName'] == "john"
        assert customer_obj['lastName'] == "doe"
        assert len(errors) == 0
    
    def test_transform_batch(self):
        """Test batch transformation"""
        data = [
            {
                "company_name": "acme corp",
                "contact_email": "john@acme.com",
                "contact_first_name": "john",
                "contact_last_name": "doe"
            },
            {
                "company_name": "beta inc",
                "contact_email": "jane@beta.com",
                "contact_first_name": "jane",
                "contact_last_name": "smith"
            }
        ]
        
        transformed_data, errors = self.transformer.transform_batch(data)
        
        assert len(transformed_data) == 2
        assert transformed_data[0]['name'] == "Acme Corp"
        assert transformed_data[1]['name'] == "Beta Inc"
        assert len(errors) == 0
    
    def test_validation_errors(self):
        """Test validation error handling"""
        row_data = {
            "company_name": "acme corp",
            "contact_email": "invalid-email",
            "contact_first_name": "john",
            "contact_last_name": "doe"
        }
        
        customer_obj, errors = self.transformer.transform_row(row_data, 1)
        
        assert len(errors) == 1
        assert errors[0]['type'] == 'validation_error'
        assert 'email' in errors[0]['message']
    
    def test_build_customer_object(self):
        """Test customer object structure"""
        data = {
            "name": "Acme Corp",
            "email": "john@acme.com",
            "firstName": "John",
            "lastName": "Doe",
            "phone": "+1-555-123-4567",
            "address": "123 Main St",
            "city": "New York",
            "country": "USA",
            "postalCode": "10001",
            "taxId": "TAX-123456",
            "companySize": "50-100"
        }
        
        customer = self.transformer.build_customer_object(data)
        
        assert customer['name'] == "Acme Corp"
        assert customer['email'] == "john@acme.com"
        assert customer['address']['street'] == "123 Main St"
        assert customer['address']['city'] == "New York"
        assert customer['metadata']['taxId'] == "TAX-123456"
        assert customer['metadata']['source'] == "csv_upload"
    
    def test_main_function(self):
        """Test the main function for Windmill integration"""
        from scripts.data_transformer import main
        
        data = [
            {
                "company_name": "acme corp",
                "contact_email": "john@acme.com",
                "contact_first_name": "john",
                "contact_last_name": "doe"
            }
        ]
        
        result = main(data, self.transformation_rules)
        
        assert 'transformed_data' in result
        assert 'errors' in result
        assert result['total_rows'] == 1
        assert len(result['transformed_data']) == 1



