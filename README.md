# MrBeast HR Analytics

A comprehensive HR analytics platform for MrBeast Industries, featuring hiring metrics, employee analytics, and data quality insights.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- PowerShell (Windows) or Bash (Linux)

### One-Command Setup (Recommended)

**For Windows:**
```bash
.\start_api.bat
```

**For Linux/Mac:**
```bash
./run_master.sh full
```

This single command will:
- ✅ Check prerequisites
- ✅ Setup virtual environment
- ✅ Install dependencies
- ✅ Setup database
- ✅ Start API and dashboard
- ✅ Open dashboard at http://localhost:8501

### Manual Setup (Alternative)

If you prefer step-by-step setup:

1. **Clone and setup:**
```bash
git clone <repository-url>
cd mrbeast-hris-analytics
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Setup database:**
```bash
# Windows
.\scripts\run_pipeline.ps1

# Linux
./scripts/run_pipeline.sh
```

4. **Start the API:**
```bash
# Windows
.\api\run_api.ps1

# Linux
./api/run_api.sh
```

5. **Launch the dashboard:**
```bash
# Windows
.\visualizations\run_dashboard.ps1

# Linux
./visualizations\run_dashboard.sh
```

6. **Access the dashboard:**
   - Open your browser to: http://localhost:8501
   - API documentation: http://localhost:8000/docs

## 📊 Features

### Core Analytics
- **Hiring Performance**: Conversion rates, time-to-hire analysis
- **Employment Types**: Full-time vs Contractor distribution
- **Salary Analysis**: By role and department with currency formatting
- **Tenure Analysis**: Employee retention insights with data quality checks
- **Data Quality**: Realistic HR data scenario analysis

### Enhanced Features
- **Role-Department Mapping**: Validated one-to-one mappings
- **Pipeline Visualization**: Hiring funnel analysis
- **Employment Source Analysis**: Application process vs direct hires
- **Hiring Success Metrics**: Detailed conversion rate analysis

## 🔧 Troubleshooting

### Common Dashboard Issues

If you encounter issues with the dashboard, here are the most common problems and solutions:

#### 1. **Minified React Error**
- **Cause**: Plotly chart rendering issues
- **Solution**: The dashboard now includes better error handling for chart rendering

#### 2. **API Error 500**
- **Cause**: Missing database views or API server issues
- **Solution**: Run the database setup script:
```bash
# Windows
.\scripts\fix_dashboard_issues.ps1

# Linux
./scripts/run_pipeline.sh
```

#### 3. **Tenure Statistics Showing Text Boxes Instead of Charts**
- **Cause**: The tenure analysis was displaying metric cards instead of proper charts
- **Solution**: Fixed in the latest version - now shows proper bar charts and box plots

#### 4. **Negative Tenures**
- **Cause**: Data quality issues with start dates
- **Solution**: The dashboard now includes data quality checks that filter out invalid dates and negative tenures

#### 5. **Missing Data**
- **Cause**: Database views not created or API endpoints not responding
- **Solution**: Check database status:
```bash
# Windows
.\scripts\check_database.ps1

# Linux
./scripts/run_pipeline.sh
```

### Quick Fix Script

For a comprehensive fix of common issues:

```bash
# Windows
.\scripts\fix_dashboard_issues.ps1

# This script will:
# 1. Check database connection
# 2. Verify required views exist
# 3. Recreate missing views if needed
# 4. Restart the API server
# 5. Provide troubleshooting guidance
```

### Manual Troubleshooting Steps

If the quick fix doesn't work:

1. **Check database connection:**
```bash
psql -h localhost -U hr_user -d mrbeast_hr -c "SELECT 1;"
```

2. **Verify required views exist:**
```bash
psql -h localhost -U hr_user -d mrbeast_hr -c "SELECT table_name FROM information_schema.views WHERE table_schema = 'hr_analytics';"
```

3. **Recreate database if needed:**
```bash
# Windows
.\scripts\clear_database.ps1
.\scripts\run_pipeline.ps1

# Linux
./scripts/clear_database.sh
./scripts/run_pipeline.sh
```

4. **Restart API server:**
```bash
# Stop any running API processes
# Then restart:
.\api\run_api.ps1  # Windows
./api/run_api.sh   # Linux
```

5. **Check API health:**
```bash
curl http://localhost:8000/health
```

### Data Quality Notes

The dashboard includes data quality checks and realistic HR scenarios:

- **Not all applicants become employees** (realistic hiring funnel)
- **Not all employees came through the application process** (direct hires, transfers, etc.)
- **Role-department mapping only works for employees who applied and were hired**
- **This is a realistic data scenario, not a data quality issue**

## 📁 Project Structure

```
mrbeast-hris-analytics/
├── api/                    # FastAPI backend
│   ├── main.py            # API endpoints
│   └── run_api.ps1/sh     # API startup scripts
├── scripts/               # Data pipeline scripts
│   ├── hr_data_pipeline.py
│   ├── run_pipeline.ps1/sh
│   ├── clear_database.ps1/sh
│   ├── check_database.ps1
│   └── fix_dashboard_issues.ps1
├── visualizations/        # Streamlit dashboard
│   ├── dashboard.py       # Main dashboard
│   └── run_dashboard.ps1/sh
├── sql/                  # Database schema
│   └── 01_schema.sql     # Enhanced schema with views
├── data/                 # Data files
├── logs/                 # Application logs
└── assets/              # Static assets
```

## 🔍 API Endpoints

- `GET /health` - Health check
- `GET /hiring-metrics` - Enhanced hiring metrics
- `GET /master-employee-view` - Comprehensive employee data
- `GET /employment-types` - Employment type distribution
- `GET /department-analytics` - Department-level analytics
- `GET /role-department-validation` - Role-department mapping validation
- `GET /data-quality-analysis` - Data quality insights
- `GET /hiring-success-analysis` - Hiring success metrics
- `GET /employee-source-analysis` - Employee source analysis

## 🛠️ Development

### Running Tests
```bash
python -m pytest tests/
```

### Adding New Features
1. Update the database schema in `sql/01_schema.sql`
2. Add API endpoints in `api/main.py`
3. Create visualizations in `visualizations/dashboard.py`
4. Update scripts as needed

### Logging
Logs are stored in the `logs/` directory:
- API logs: `logs/api.log`
- Pipeline logs: `logs/pipeline.log`
- Dashboard logs: `logs/dashboard.log`

## 📈 Analytics Features

### Hiring Analytics
- Conversion rates by role and department
- Time-to-hire analysis
- Pipeline stage visualization
- Hiring success metrics

### Employee Analytics
- Employment type distribution
- Salary analysis by role and department
- Tenure analysis with data quality checks
- Employee source analysis

### Data Quality
- Realistic HR data scenario analysis
- Role-department mapping validation
- Data coverage comparison
- Quality insights and warnings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details. 