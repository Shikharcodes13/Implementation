# CSV Upload System with Windmill

A comprehensive CSV processing system built on Windmill that provides customizable data transformation pipelines and integrates with mock API services for customer creation.

## 🏗️ Architecture Overview

This system consists of several interconnected Windmill flows and scripts:

1. **CSV Upload Flow** - Handles file uploads and validation
2. **Data Transformation Pipeline** - Customizable transformation scripts
3. **API Integration** - Mock customer creation service
4. **Error Handling & Reporting** - Comprehensive error tracking and reporting

## 📋 Features

- ✅ CSV file upload and parsing
- ✅ Configurable data transformation rules
- ✅ Row-level error handling
- ✅ Comprehensive processing reports
- ✅ API integration with retry logic
- ✅ Extensible transformation pipeline

## 🚀 Quick Start

### Prerequisites

- Windmill installed locally
- Python 3.8+ (for local testing)
- Node.js 16+ (for local testing)

### Installation

1. **Install Windmill**
   ```bash
   # Using npm
   npm install -g @windmill-labs/windmill
   
   # Or using Docker
   docker run -it --rm -p 8000:8000 windmill/windmill:latest
   ```

2. **Start Windmill**
   ```bash
   windmill start
   ```

3. **Access the UI**
   Open http://localhost:8000 in your browser

### Project Setup

1. Import the flows and scripts from this repository
2. Create a workspace called "csv-upload-system"
3. Import all the provided flows and scripts

## 📁 Project Structure

```
csv-upload-system/
├── flows/
│   ├── csv_upload_flow.json          # Main CSV processing flow
│   ├── data_transformation_flow.json # Transformation pipeline
│   └── error_reporting_flow.json     # Error handling flow
├── scripts/
│   ├── csv_parser.py                 # CSV parsing and validation
│   ├── data_transformer.py           # Core transformation logic
│   ├── customer_api_client.py        # Mock API integration
│   ├── error_handler.py              # Error processing
│   └── report_generator.py           # Report generation
├── sample_data/
│   └── customers.csv                 # Sample CSV data
├── config/
│   └── transformation_rules.json     # Transformation configuration
├── docs/
│   ├── setup_guide.md               # Detailed setup instructions
│   ├── transformation_guide.md      # How to customize transformations
│   └── api_integration.md           # API integration details
├── requirements.txt                  # Python dependencies
└── package.json                     # Node.js dependencies
```

## 🔧 Configuration

### Transformation Rules

The system uses a JSON configuration file to define transformation rules. This allows easy modification without code changes:

```json
{
  "field_mappings": {
    "company_name": "name",
    "contact_email": "email",
    "contact_first_name": "firstName",
    "contact_last_name": "lastName"
  },
  "validations": {
    "email": "email_format",
    "phone": "phone_format"
  },
  "transformations": {
    "name": "title_case",
    "phone": "normalize_phone"
  }
}
```

## 📊 Sample Data Format

### Input CSV
```csv
company_name,contact_email,contact_first_name,contact_last_name,phone_number,address,city,country,postal_code,tax_id,company_size
Acme Corp,john.doe@acme.com,John,Doe,+1-555-0100,123 Business St,New York,USA,10001,TAX-123456,50-100
Beta Inc,jane@beta.co,Jane,Smith,555.0200,456 Commerce Ave,San Francisco,USA,94105,TAX-789012,100-500
```

### Output Customer Object
```json
{
  "name": "Acme Corp",
  "email": "john.doe@acme.com",
  "firstName": "John",
  "lastName": "Doe",
  "phone": "+1-555-0100",
  "address": {
    "street": "123 Business St",
    "city": "New York",
    "country": "USA",
    "postalCode": "10001"
  },
  "metadata": {
    "taxId": "TAX-123456",
    "companySize": "50-100"
  }
}
```

## 🔄 Workflow

1. **Upload**: User uploads CSV file through Windmill UI
2. **Parse**: System validates and parses CSV data
3. **Transform**: Data is transformed using configurable rules
4. **Validate**: Each row is validated for business rules
5. **API Call**: Valid records are sent to customer API
6. **Report**: Processing results are generated and displayed

## 🛠️ Customization

### Adding New Transformations

1. Edit `transformation_rules.json`
2. Add new transformation functions to `data_transformer.py`
3. Update field mappings as needed

### Custom Validation Rules

1. Add validation functions to `data_transformer.py`
2. Update the validation configuration
3. Test with sample data

## 📈 Monitoring & Reporting

The system provides comprehensive reporting:

- **Processing Summary**: Total rows, success/failure counts
- **Error Details**: Specific errors per row
- **Performance Metrics**: Processing time, API response times
- **Data Quality**: Validation results and data issues

## 🔒 Security

- Input validation and sanitization
- Secure API key management
- Error message sanitization
- Rate limiting for API calls

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run tests
python -m pytest tests/
```

## 📚 Documentation

- [Setup Guide](docs/setup_guide.md) - Detailed installation instructions
- [Transformation Guide](docs/transformation_guide.md) - Customizing transformations
- [API Integration](docs/api_integration.md) - API setup and configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
- Check the documentation
- Review error logs in Windmill
- Create an issue in the repository

---

**Built with ❤️ using Windmill**

