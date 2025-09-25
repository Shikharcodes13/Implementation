# CSV Upload System Setup Guide

## Prerequisites

- Windmill installed locally
- Python 3.8+ 
- Node.js 16+
- Git

## Step 1: Install Windmill

### Option 1: Using npm (Recommended)
```bash
npm install -g @windmill-labs/windmill
```

### Option 2: Using Docker
```bash
docker run -it --rm -p 8000:8000 windmill/windmill:latest
```

### Option 3: From Source
```bash
git clone https://github.com/windmill-labs/windmill.git
cd windmill
npm install
npm run build
```

## Step 2: Start Windmill

```bash
windmill start
```

The Windmill UI will be available at http://localhost:8000

## Step 3: Create Workspace

1. Open Windmill UI
2. Create a new workspace called "csv-upload-system"
3. Navigate to the workspace

## Step 4: Import Scripts

1. Go to Scripts section
2. Create new Python scripts for each component:
   - `scripts/csv_parser.py`
   - `scripts/data_transformer.py`
   - `scripts/customer_api_client.py`
   - `scripts/error_handler.py`
   - `scripts/report_generator.py`

### Script Creation Steps:
1. Click "Create Script"
2. Choose "Python" as language
3. Copy the content from the corresponding script file
4. Save with the exact path name (e.g., `scripts/csv_parser`)

## Step 5: Import Flows

1. Go to Flows section
2. Create the main flow: `csv_upload_flow.json`
3. Configure the flow modules and connections

### Flow Creation Steps:
1. Click "Create Flow"
2. Name it "CSV Upload Flow"
3. Add modules by clicking the "+" button
4. Configure each module:
   - Set the script path
   - Configure input transforms
   - Connect modules with arrows

## Step 6: Configure API

### Option 1: Use Mock API Service
Use a service like JSONPlaceholder or create a simple mock endpoint.

### Option 2: Create Mock API in Windmill
Create a simple REST API script in Windmill that accepts customer data.

#### Mock API Script Example:
```python
def main(customer_data: dict) -> dict:
    """Mock API endpoint for customer creation"""
    return {
        "id": f"customer_{hash(str(customer_data)) % 10000}",
        "status": "created",
        "data": customer_data,
        "created_at": "2024-01-01T00:00:00Z"
    }
```

## Step 7: Test the System

1. Upload a sample CSV file using the sample data provided
2. Run the flow
3. Review the processing report

### Testing Steps:
1. Go to the CSV Upload Flow
2. Click "Run Flow"
3. Upload `sample_data/customers.csv`
4. Monitor the execution
5. Review the final report

## Step 8: Configure Transformation Rules

1. Edit `config/transformation_rules.json`
2. Modify field mappings as needed
3. Add custom validation rules
4. Configure API settings

## Troubleshooting

### Common Issues

1. **CSV Encoding Issues**
   - Ensure CSV files are saved as UTF-8
   - Use the encoding detection feature
   - Check file encoding in a text editor

2. **API Connection Issues**
   - Verify API URL and authentication
   - Check network connectivity
   - Test API endpoint manually

3. **Transformation Errors**
   - Review transformation rules configuration
   - Check field mappings
   - Validate input data format

4. **Flow Execution Issues**
   - Check script paths are correct
   - Verify input transforms
   - Review error logs

### Debug Mode

Enable debug logging by setting the log level to DEBUG in Windmill configuration.

1. Go to Settings
2. Find Logging Configuration
3. Set level to DEBUG
4. Restart Windmill

### Performance Issues

1. **Large CSV Files**
   - Increase batch size in API configuration
   - Enable parallel processing
   - Consider file chunking

2. **Slow API Calls**
   - Reduce batch size
   - Increase timeout settings
   - Check API server performance

## Advanced Configuration

### Custom Transformations

1. Add new transformation functions to `data_transformer.py`
2. Update `transformation_rules.json`
3. Test with sample data

### Custom Validations

1. Add validation functions to `data_transformer.py`
2. Update validation configuration
3. Test edge cases

### Multiple API Endpoints

1. Configure multiple API endpoints in `api_config.json`
2. Add endpoint selection logic
3. Implement failover mechanisms

## Security Considerations

1. **API Keys**
   - Store in environment variables
   - Use Windmill secrets management
   - Rotate keys regularly

2. **Data Privacy**
   - Sanitize error messages
   - Log minimal sensitive data
   - Implement data retention policies

3. **Input Validation**
   - Validate file types and sizes
   - Sanitize CSV content
   - Implement rate limiting

## Monitoring and Maintenance

### Logging
- Enable comprehensive logging
- Set up log aggregation
- Monitor error rates

### Performance Monitoring
- Track processing times
- Monitor API response times
- Set up alerts for failures

### Regular Maintenance
- Update dependencies
- Review and optimize transformation rules
- Clean up old logs and data

## Support and Resources

- Windmill Documentation: https://docs.windmill.dev
- GitHub Repository: Link to your repo
- Issue Tracker: Link to issues
- Community Forum: Link to forum

## Next Steps

1. Customize transformation rules for your use case
2. Set up monitoring and alerting
3. Create additional flows for different data types
4. Implement user authentication and authorization
5. Add data visualization and reporting features



