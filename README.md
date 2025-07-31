# MrBeast HR Analytics Platform

HR analytics platform integrating recruiting and payroll data with REST API and interactive dashboard.

## Overview

This project demonstrates a complete HR data pipeline that:
- Loads data from multiple HR systems into PostgreSQL
- Transforms data using SQL with time-to-hire calculations
- Serves cleaned data via FastAPI REST endpoints
- Visualizes insights through Streamlit dashboard
- Automates daily data refresh with cron scheduling

## Requirements

- Python 3.8+
- PostgreSQL 12+
- PowerShell (Windows) or Bash (Linux)

## Quick Start

### Windows
```bash
.\start_api.bat
```

### Linux/Mac
```bash
./run_master.sh full
```

The dashboard will be available at http://localhost:8501

## Manual Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Setup database:
```bash
# Windows
.\scripts\run_pipeline.ps1

# Linux
./scripts/run_pipeline.sh
```

3. Start API:
```bash
# Windows
.\api\run_api.ps1

# Linux
.\api\run_api.sh
```

4. Start dashboard:
```bash
# Windows
.\visualizations\run_dashboard.ps1

# Linux
.\visualizations\run_dashboard.sh
```

## API Endpoints

### Required Endpoints
- `GET /hiring-metrics` - Time-to-hire by department
- `GET /applicants/status-summary` - Applicant counts by status

### Additional Endpoints
- `GET /master-employee-view` - Employee data
- `GET /employment-types` - Employment type distribution
- `GET /department-analytics` - Department analytics
- `GET /data-quality-analysis` - Data quality insights
- `GET /hiring-success-analysis` - Hiring success metrics
- `GET /employee-source-analysis` - Employee source analysis
- `GET /health` - System health check

## Database Schema

The platform uses PostgreSQL with the following key tables:
- `hr_analytics.employees` - Employee data
- `hr_analytics.applicants` - Applicant data
- `hr_analytics.employment_types` - Employment type data
- `hr_analytics.role_department_mapping` - Role-department mappings

Analytics views provide:
- Time-to-hire calculations
- Hiring conversion rates
- Employee tenure analysis
- Data quality metrics

## Data Pipeline

The ETL process:
1. Extracts data from Excel files
2. Cleans and standardizes data
3. Loads into PostgreSQL
4. Creates analytics views
5. Runs daily via cron: `0 2 * * * /path/to/scripts/daily_pipeline.sh`

## Architecture

### Backend
- **FastAPI**: High-performance async API
- **SQLAlchemy**: Database ORM
- **PostgreSQL**: Primary database

### Frontend
- **Streamlit**: Interactive dashboard
- **Plotly**: Data visualizations

### Infrastructure
- **Docker**: Containerization
- **Cron**: Daily automation
- **Logging**: Application monitoring

## Configuration

### Environment Variables
```bash
DATABASE_URL=postgresql://hr_user:hr_password@localhost:5432/mrbeast_hr
```

### Database Setup
```sql
CREATE DATABASE mrbeast_hr;
CREATE USER hr_user WITH PASSWORD 'hr_password';
GRANT ALL PRIVILEGES ON DATABASE mrbeast_hr TO hr_user;
```

## Development

### Project Structure
```
mrbeast-hris-analytics/
├── api/                    # FastAPI backend
├── scripts/               # Data pipeline
├── visualizations/        # Streamlit dashboard
├── sql/                  # Database schema
├── data/                 # Data files
└── assets/              # Static assets
```

### Adding New Features
1. Update schema in `sql/01_schema.sql`
2. Add endpoints in `api/main.py`
3. Create visualizations in `visualizations/dashboard.py`
4. Update pipeline scripts as needed

## Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
psql -h localhost -U hr_user -d mrbeast_hr -c "SELECT 1;"
```

**API Not Starting**
```bash
# Check environment
echo $DATABASE_URL
# Should be: postgresql://hr_user:hr_password@localhost:5432/mrbeast_hr
```

**Dashboard Issues**
- Clear browser cache
- Verify API is running on port 8000
- Check database views are created

**Virtual Environment**
```bash
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```

## Deployment

### Docker
```bash
docker-compose up -d
```

### Production
- Use service management scripts
- Configure logging
- Set up monitoring

## Design Decisions

### Technology Stack
- **FastAPI**: Performance and auto-documentation
- **Streamlit**: Rapid dashboard development
- **PostgreSQL**: ACID compliance and analytics
- **Docker**: Consistent deployment

### Data Model
- Handles realistic HR data gaps
- Graceful degradation with missing data
- Validated role-department mappings

### API Design
- RESTful conventions
- Comprehensive error handling
- Basic authentication
- Caching for performance

## Evaluation Criteria

### API Design
- RESTful standards
- Error handling (404s, 500s)
- Scalable architecture

### Code Quality
- Well-structured code
- Reproducible setup
- Modular architecture

### Database Design
- Normalized schema
- SQL transformations
- Realistic data handling

### Automation
- Cron scheduling
- Comprehensive logging
- Error recovery

### Visualization
- Interactive charts
- Leadership metrics
- Real-time updates

### Documentation
- Setup instructions
- Design decisions
- Assumptions documented

## Bonus Features

- Basic authentication
- Docker containerization
- Basic alerting
- Professional code structure

## Assumptions & Limitations

### Data Assumptions
- Name matching between applicants and employees
- Role-department mapping from employee data
- Daily data refresh sufficient for analytics
- Standardized status values across data sources

### Technical Limitations
- Basic authentication (not JWT)
- No role-based access control
- Limited audit logging
- No data encryption at rest

### Known Issues
- Some applicants don't match to employees due to name variations
- Time-to-hire doesn't account for offer negotiations
- Current design optimized for demo scale
- Daily batch processing (not real-time)

## License

MIT License

---

*Documentation formatting derived from standard technical documentation best practices. Layout and structure overview provided by Claude AI assistant.*