# CSV Upload System - Setup Guide

## 🚀 Quick Start with Windmill

### Step 1: Windmill is Running ✅

Windmill is now running in Docker at: **http://localhost:8000**

You can access the Windmill UI by opening your browser and navigating to:
```
http://localhost:8000
```

### Step 2: Access Windmill UI

1. **Open your browser** and go to `http://localhost:8000`
2. **Login**: Use the default credentials (or create a new account)
3. **Create a workspace** called "csv-upload-system"

### Step 3: Import Scripts and Flows

#### Option A: Manual Import (Recommended for first-time setup)

1. **Navigate to Scripts** in the Windmill UI
2. **Create each script** by copying the content from our files:

##### Core Scripts to Create:

1. **CSV Parser** (`scripts/csv_parser.py`)
   - Path: `scripts/csv_parser`
   - Language: Python 3
   - Copy content from `scripts/csv_parser.py`

2. **Data Transformer** (`scripts/data_transformer.py`)
   - Path: `scripts/data_transformer`
   - Language: Python 3
   - Copy content from `scripts/data_transformer.py`

3. **Customer API Client** (`scripts/customer_api_client.py`)
   - Path: `scripts/customer_api_client`
   - Language: Python 3
   - Copy content from `scripts/customer_api_client.py`

4. **Error Handler** (`scripts/error_handler.py`)
   - Path: `scripts/error_handler`
   - Language: Python 3
   - Copy content from `scripts/error_handler.py`

5. **Report Generator** (`scripts/report_generator.py`)
   - Path: `scripts/report_generator`
   - Language: Python 3
   - Copy content from `scripts/report_generator.py`

6. **Mock Customer API** (`scripts/mock_customer_api.py`)
   - Path: `scripts/mock_customer_api`
   - Language: Python 3
   - Copy content from `scripts/mock_customer_api.py`

7. **Main Flow** (`scripts/main_flow.py`)
   - Path: `scripts/main_flow`
   - Language: Python 3
   - Copy content from `scripts/main_flow.py`

#### Option B: Using Local Development (Advanced)

If you want to use the local development approach:

1. **Install Windmill CLI** (when available for Windows):
   ```bash
   # This will be available once Windmill CLI is properly installed
   wmill workspace add csv-upload-system [workspace_id] [remote]
   wmill sync pull
   ```

2. **Push scripts to Windmill**:
   ```bash
   wmill sync push
   ```

### Step 4: Create Flows

1. **Navigate to Flows** in the Windmill UI
2. **Create the main flow**:

#### Main CSV Upload Flow

Create a new flow called "CSV Upload Flow" and configure the modules:

```yaml
# Flow Configuration
summary: "Main CSV processing pipeline"
description: "Processes CSV files through transformation and API integration"

modules:
  - id: "csv_parser"
    type: "script"
    path: "scripts/csv_parser"
    input_transforms:
      file_content: "result.file_content"
      delimiter: "result.delimiter"
      required_fields: "result.required_fields"

  - id: "data_transformer"
    type: "script"
    path: "scripts/data_transformer"
    input_transforms:
      data: "csv_parser.data"
      transformation_rules: "result.transformation_rules"

  - id: "customer_api_client"
    type: "script"
    path: "scripts/customer_api_client"
    input_transforms:
      customers: "data_transformer.transformed_data"
      api_base_url: "result.api_base_url"
      api_key: "result.api_key"
      batch_size: "result.batch_size"

  - id: "error_handler"
    type: "script"
    path: "scripts/error_handler"
    input_transforms:
      errors: "result.all_errors"
      original_data: "csv_parser.data"

  - id: "report_generator"
    type: "script"
    path: "scripts/report_generator"
    input_transforms:
      processing_summary: "result.processing_summary"
      data_quality: "result.data_quality"
      api_results: "customer_api_client"
      errors: "error_handler"
      transformed_data: "data_transformer.transformed_data"
      processing_time: "result.processing_time"

failure_module: "error_handler"
```

### Step 5: Test the System

1. **Use the sample data** from `sample_data/customers.csv`:

```csv
company_name,contact_email,contact_first_name,contact_last_name,phone_number,address,city,country,postal_code,tax_id,company_size
Acme Corp,john.doe@acme.com,John,Doe,+1-555-0100,123 Business St,New York,USA,10001,TAX-123456,50-100
Beta Inc,jane@beta.co,Jane,Smith,555.0200,456 Commerce Ave,San Francisco,USA,94105,TAX-789012,100-500
```

2. **Run the flow**:
   - Go to the "CSV Upload Flow"
   - Click "Run Flow"
   - Upload the CSV file
   - Monitor the execution
   - Review the results

### Step 6: Configure API Integration

#### Option 1: Use Mock API (Recommended for testing)

The system includes a mock API that simulates customer creation:

```python
# The mock API is already configured in scripts/mock_customer_api.py
# It simulates API responses and includes error scenarios for testing
```

#### Option 2: Connect to Real API

To connect to a real API:

1. **Update API configuration** in the flow parameters:
   - `api_base_url`: Your API endpoint
   - `api_key`: Your API authentication key
   - `batch_size`: Number of records to process per batch

2. **Test the connection**:
   - Run a small test with 1-2 records
   - Verify authentication works
   - Check error handling

### Step 7: Customize Transformation Rules

Edit the transformation rules by modifying the flow parameters or the data transformer script:

```python
# Example customization in data_transformer.py
transformation_rules = {
    "field_mappings": {
        "company_name": "name",
        "contact_email": "email",
        # Add your custom field mappings here
    },
    "validations": {
        "email": "email_format",
        "phone": "phone_format",
        # Add your custom validations here
    },
    "transformations": {
        "name": "title_case",
        "phone": "normalize_phone",
        # Add your custom transformations here
    }
}
```

## 🛠️ Troubleshooting

### Common Issues

1. **Windmill not accessible**
   - Check if Docker is running
   - Verify port 8000 is not blocked
   - Try: `docker ps` to see running containers

2. **Script execution errors**
   - Check Python syntax in scripts
   - Verify all imports are available
   - Review error logs in Windmill UI

3. **API connection issues**
   - Test API endpoint manually
   - Verify authentication credentials
   - Check network connectivity

### Debug Mode

Enable debug logging in Windmill:
1. Go to Settings → Logging
2. Set log level to DEBUG
3. Restart Windmill if needed

## 📚 Next Steps

1. **Test with your own CSV data**
2. **Customize transformation rules** for your business needs
3. **Connect to your actual CRM API**
4. **Set up monitoring and alerting**
5. **Create additional flows** for different data types

## 🔗 Useful Links

- [Windmill Documentation](https://docs.windmill.dev)
- [Local Development Guide](https://www.windmill.dev/docs/advanced/local_development)
- [Script Development](https://docs.windmill.dev/docs/core_concepts/scripts)
- [Flow Development](https://docs.windmill.dev/docs/core_concepts/flows)

---

**🎉 Your CSV Upload System is ready to use!**

Follow the steps above to get started with your customized CSV processing pipeline.



