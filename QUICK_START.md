# 🚀 CSV Upload System - Quick Start

## Current Status: Windmill is Starting Up

Windmill is currently starting in Docker. It should be ready in a few minutes.

## ✅ What's Ready

- ✅ **Project Structure**: Complete CSV upload system implemented
- ✅ **All Scripts**: 7 Python scripts ready for import
- ✅ **Flow Configurations**: 3 Windmill flows ready to use
- ✅ **Sample Data**: Test CSV files included
- ✅ **Documentation**: Comprehensive guides created

## 🎯 Next Steps (Once Windmill is Ready)

### 1. Access Windmill UI
```
URL: http://localhost:8000
```

### 2. Create Workspace
- Name: `csv-upload-system`
- Type: Standard workspace

### 3. Import Scripts (In Order)

| Script | Path | Purpose |
|--------|------|---------|
| CSV Parser | `scripts/csv_parser` | Parse and validate CSV files |
| Data Transformer | `scripts/data_transformer` | Transform data with business rules |
| Customer API Client | `scripts/customer_api_client` | Send data to APIs with retry logic |
| Error Handler | `scripts/error_handler` | Process and categorize errors |
| Report Generator | `scripts/report_generator` | Generate processing reports |
| Mock Customer API | `scripts/mock_customer_api` | Test API for development |
| Main Flow | `scripts/main_flow` | Orchestrate entire process |

### 4. Create Main Flow

**Flow Name**: `CSV Upload Flow`

**Modules** (in order):
1. CSV Parser → 2. Data Transformer → 3. Customer API Client → 4. Error Handler → 5. Report Generator

### 5. Test with Sample Data

Use `sample_data/customers.csv`:
```csv
company_name,contact_email,contact_first_name,contact_last_name,phone_number,address,city,country,postal_code,tax_id,company_size
Acme Corp,john.doe@acme.com,John,Doe,+1-555-0100,123 Business St,New York,USA,10001,TAX-123456,50-100
```

## 🔧 Configuration Options

### MockAPI Configuration

#### Default MockAPI Endpoints
- **Primary**: `https://jsonplaceholder.typicode.com/users`
- **Alternative**: `https://reqres.in/api/users`
- **Testing**: `https://httpbin.org/post`

#### API Configuration
```json
{
  "mock_api": {
    "base_url": "https://jsonplaceholder.typicode.com",
    "endpoints": {
      "customers": "/users",
      "health": "/posts/1"
    },
    "authentication": {
      "type": "none"
    },
    "settings": {
      "timeout": 30,
      "batch_size": 10,
      "retry_attempts": 3
    }
  }
}
```

#### Built-in Mock API Testing
The system includes `scripts/mock_customer_api.py` for local testing:
- **Endpoint**: Use as Windmill script
- **Features**: Validation, error simulation, unique ID generation
- **Testing**: 5% random failure rate for realistic testing

### Transformation Rules
```json
{
  "field_mappings": {
    "company_name": "name",
    "contact_email": "email"
  },
  "transformations": {
    "name": "title_case",
    "phone": "normalize_phone"
  }
}
```

## 🚨 Troubleshooting

### Windmill Not Loading?
1. Check Docker is running: `docker ps`
2. Wait 2-3 minutes for startup
3. Try: `http://localhost:8000`

### Script Import Issues?
1. Check Python syntax
2. Verify file paths
3. Review error logs in Windmill UI

## 📞 Support

- **Setup Guide**: See `SETUP_GUIDE.md`
- **Documentation**: See `docs/` folder
- **Sample Data**: See `sample_data/` folder

---

**🎉 Ready to process CSV data with customizable transformations!**



