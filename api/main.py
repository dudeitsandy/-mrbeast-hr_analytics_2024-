#!/usr/bin/env python3
"""
MrBeast HR Analytics API
FastAPI backend for HR analytics data
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine, text
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import secrets

# Create FastAPI app
app = FastAPI(
    title="MrBeast HR Analytics API",
    description="REST API for MrBeast HR Analytics Platform",
    version="1.0.0"
)



# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic Authentication
security = HTTPBasic()

# Simple user credentials (in production, use environment variables)
USERS = {
    "mrbeast": "hr_analytics_2024",
    "admin": "admin_password"
}

# Development mode - disable authentication for local development
DEV_MODE = os.getenv("DEV_MODE", "true").lower() == "true"

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """Validate basic authentication"""
    # Skip authentication in development mode
    if DEV_MODE:
        return "dev_user"
    
    # If no credentials provided in dev mode, still allow access
    if DEV_MODE and not credentials:
        return "dev_user"
    
    username = credentials.username
    password = credentials.password
    
    if username not in USERS or not secrets.compare_digest(password, USERS[username]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return username

# Database connection
def get_database_engine():
    """Get database engine"""
    database_url = os.getenv("DATABASE_URL", "postgresql://hr_user:hr_password@localhost:5432/mrbeast_hr")
    return create_engine(database_url)

# Cache for API responses (5 minutes)
CACHE = {}  # Clear cache on restart
CACHE_DURATION = 300  # 5 minutes

def get_cached_data(key: str) -> Optional[Dict]:
    """Get cached data if not expired"""
    if key in CACHE:
        timestamp, data = CACHE[key]
        if datetime.now() - timestamp < timedelta(seconds=CACHE_DURATION):
            return data
    return None

def set_cached_data(key: str, data: Dict):
    """Set cached data with timestamp"""
    CACHE[key] = (datetime.now(), data)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        engine = get_database_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/hiring-metrics")
async def get_hiring_metrics(username: str = Depends(get_current_user) if not DEV_MODE else None):
    """Get hiring metrics with authentication"""
    cache_key = "hiring_metrics"
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return cached_data
    
    try:
        engine = get_database_engine()
        
        # Get hiring metrics from database
        query = """
        SELECT 
            "Role" as role,
            department,
            total_applicants,
            hired_count,
            conversion_rate,
            avg_time_to_hire_days as avg_time_to_hire
        FROM hr_analytics.enhanced_hiring_metrics
        ORDER BY conversion_rate DESC
        """
        
        df = pd.read_sql(query, engine)
        
        # Convert to JSON-serializable format
        metrics = df.to_dict('records')
        
        result = {
            "metrics": metrics,
            "summary": {
                "total_roles": len(metrics),
                "avg_conversion_rate": round(df['conversion_rate'].mean(), 2),
                "avg_time_to_hire": round(df['avg_time_to_hire'].mean(), 1)
            }
        }
        
        set_cached_data(cache_key, result)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch hiring metrics: {str(e)}")

@app.get("/applicants/status-summary")
async def get_applicants_status_summary(username: str = Depends(get_current_user) if not DEV_MODE else None):
    """Get applicants status summary with authentication"""
    cache_key = "applicants_status_summary"
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return cached_data
    
    try:
        engine = get_database_engine()
        
        query = """
        SELECT 
            "Status" as status,
            COUNT(*) as count,
            ROUND((COUNT(*) * 100.0) / SUM(COUNT(*)) OVER (), 2) as percentage
        FROM hr_analytics.applicants
        GROUP BY "Status"
        ORDER BY count DESC
        """
        
        df = pd.read_sql(query, engine)
        result = df.to_dict('records')
        
        set_cached_data(cache_key, result)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch applicants status summary: {str(e)}")

@app.get("/master-employee-view")
async def get_master_employee_view(username: str = Depends(get_current_user) if not DEV_MODE else None):
    """Get master employee view with authentication"""
    print("DEBUG: Master employee view endpoint called")  # Debug log
    
    cache_key = "master_employee_view"
    cached_data = get_cached_data(cache_key)
    if cached_data:
        print("DEBUG: Returning cached data")  # Debug log
        return cached_data
    
    try:
        print("DEBUG: Getting database engine")  # Debug log
        engine = get_database_engine()
        
        query = """
        SELECT 
            "ID",
            "Name",
            "Salary",
            "Department",
            "Start Date",
            "End Date",
            "Employment Type",
            applied_role,
            "Application Date",
            application_status,
            employment_status,
            days_to_hire
        FROM hr_analytics.master_employee_view
        ORDER BY "ID"
        """
        
        print("DEBUG: Executing query")  # Debug log
        df = pd.read_sql(query, engine)
        print(f"DEBUG: Query returned {len(df)} rows")  # Debug log
        
        # Convert datetime objects to strings for JSON serialization
        print("DEBUG: Converting datetime columns")  # Debug log
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns]':
                print(f"DEBUG: Converting column {col}")  # Debug log
                df[col] = df[col].dt.strftime('%Y-%m-%d')
        
        # Handle NaN values for JSON serialization
        print("DEBUG: Handling NaN values")  # Debug log
        df = df.replace({pd.NA: None, pd.NaT: None})
        df = df.where(pd.notnull(df), None)
        
        # Additional NaN handling for all data types
        for col in df.columns:
            df[col] = df[col].replace([float('nan'), float('inf'), float('-inf')], None)
        
        print("DEBUG: Converting to dict")  # Debug log
        result = df.to_dict('records')
        print(f"DEBUG: Converted to {len(result)} records")  # Debug log
        
        set_cached_data(cache_key, result)
        print("DEBUG: Returning result")  # Debug log
        return {"employees": result}
        
    except Exception as e:
        print(f"DEBUG: Exception occurred: {e}")  # Debug log
        import traceback
        error_details = f"Failed to fetch master employee view: {str(e)}\nTraceback: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_details)

@app.get("/employment-types")
async def get_employment_types(username: str = Depends(get_current_user) if not DEV_MODE else None):
    """Get employment types distribution with authentication"""
    cache_key = "employment_types"
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return cached_data
    
    try:
        engine = get_database_engine()
        
        query = """
        SELECT 
            "Employment Type",
            COUNT(*) as count,
            ROUND((COUNT(*) * 100.0) / SUM(COUNT(*)) OVER (), 2) as percentage
        FROM hr_analytics."Employment type"
        GROUP BY "Employment Type"
        ORDER BY count DESC
        """
        
        df = pd.read_sql(query, engine)
        result = df.to_dict('records')
        
        set_cached_data(cache_key, result)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch employment types: {str(e)}")

@app.get("/department-analytics")
async def get_department_analytics(username: str = Depends(get_current_user) if not DEV_MODE else None):
    """Get department analytics with authentication"""
    cache_key = "department_analytics"
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return cached_data
    
    try:
        engine = get_database_engine()
        
        query = """
        SELECT 
            "Department",
            COUNT(*) as employee_count,
            AVG("Salary") as avg_salary,
            COUNT(CASE WHEN "End Date" IS NULL THEN 1 END) as current_employees
        FROM hr_analytics.employees
        GROUP BY "Department"
        ORDER BY employee_count DESC
        """
        
        df = pd.read_sql(query, engine)
        result = df.to_dict('records')
        
        set_cached_data(cache_key, result)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch department analytics: {str(e)}")

@app.get("/role-department-validation")
async def get_role_department_validation(username: str = Depends(get_current_user) if not DEV_MODE else None):
    """Get role-department mapping validation with authentication"""
    cache_key = "role_department_validation"
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return cached_data
    
    try:
        engine = get_database_engine()
        
        query = """
        SELECT 
            "Role",
            "Department",
            "Confidence_Score",
            "Mapping_Type",
            "Validation_Status"
        FROM hr_analytics.role_department_mapping
        ORDER BY "Confidence_Score" DESC
        """
        
        df = pd.read_sql(query, engine)
        result = df.to_dict('records')
        
        set_cached_data(cache_key, result)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch role-department validation: {str(e)}")

@app.get("/data-quality-analysis")
async def get_data_quality_analysis(username: str = Depends(get_current_user) if not DEV_MODE else None):
    """Get data quality analysis with authentication"""
    cache_key = "data_quality_analysis"
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return cached_data
    
    try:
        engine = get_database_engine()
        
        # Check data quality metrics
        quality_checks = {}
        
        # Check for missing data
        missing_data_query = """
        SELECT 
            'applicants' as table_name,
            COUNT(*) as total_records,
            COUNT(CASE WHEN "Name" IS NULL OR "Name" = '' THEN 1 END) as missing_names,
            COUNT(CASE WHEN "Role" IS NULL OR "Role" = '' THEN 1 END) as missing_roles
        FROM hr_analytics.applicants
        UNION ALL
        SELECT 
            'employees' as table_name,
            COUNT(*) as total_records,
            COUNT(CASE WHEN "Name" IS NULL OR "Name" = '' THEN 1 END) as missing_names,
            COUNT(CASE WHEN "Department" IS NULL OR "Department" = '' THEN 1 END) as missing_departments
        FROM hr_analytics.employees
        """
        
        df = pd.read_sql(missing_data_query, engine)
        quality_checks['missing_data'] = df.to_dict('records')
        
        # Check for data consistency
        consistency_query = """
        SELECT 
            COUNT(DISTINCT a."Name") as applicants_with_names,
            COUNT(DISTINCT e."Name") as employees_with_names,
            COUNT(DISTINCT CASE WHEN a."Name" = e."Name" THEN a."Name" END) as matching_names
        FROM hr_analytics.applicants a
        FULL OUTER JOIN hr_analytics.employees e ON a."Name" = e."Name"
        """
        
        df = pd.read_sql(consistency_query, engine)
        quality_checks['consistency'] = df.to_dict('records')[0]
        
        set_cached_data(cache_key, quality_checks)
        return quality_checks
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data quality analysis: {str(e)}")

@app.get("/hiring-success-analysis")
async def get_hiring_success_analysis(username: str = Depends(get_current_user) if not DEV_MODE else None):
    """Get hiring success analysis with authentication"""
    cache_key = "hiring_success_analysis"
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return cached_data
    
    try:
        engine = get_database_engine()
        
        query = """
        SELECT 
            role,
            department,
            total_applicants,
            hired_count,
            ROUND((hired_count * 100.0) / total_applicants, 2) as success_rate,
            AVG(time_to_hire_days) as avg_time_to_hire
        FROM hr_analytics.enhanced_hiring_metrics
        WHERE total_applicants > 0
        ORDER BY success_rate DESC
        """
        
        df = pd.read_sql(query, engine)
        result = df.to_dict('records')
        
        set_cached_data(cache_key, result)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch hiring success analysis: {str(e)}")

@app.get("/employee-source-analysis")
async def get_employee_source_analysis(username: str = Depends(get_current_user) if not DEV_MODE else None):
    """Get employee source analysis with authentication"""
    cache_key = "employee_source_analysis"
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return cached_data
    
    try:
        engine = get_database_engine()
        
        query = """
        SELECT 
            CASE 
                WHEN a."Name" IS NOT NULL THEN 'Application Process'
                ELSE 'Direct Hire/Transfer'
            END as source_type,
            COUNT(*) as count,
            ROUND((COUNT(*) * 100.0) / SUM(COUNT(*)) OVER (), 2) as percentage
        FROM hr_analytics.employees e
        LEFT JOIN hr_analytics.applicants a ON e."Name" = a."Name" AND a."Status" = 'Hired'
        GROUP BY 
            CASE 
                WHEN a."Name" IS NOT NULL THEN 'Application Process'
                ELSE 'Direct Hire/Transfer'
            END
        ORDER BY count DESC
        """
        
        df = pd.read_sql(query, engine)
        result = df.to_dict('records')
        
        set_cached_data(cache_key, result)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch employee source analysis: {str(e)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MrBeast HR Analytics API")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    
    args = parser.parse_args()
    
    print(f"Starting MrBeast HR Analytics API on {args.host}:{args.port}")
    print(f"API Documentation: http://{args.host}:{args.port}/docs")
    print(f"Health Check: http://{args.host}:{args.port}/health")
    
    uvicorn.run(app, host=args.host, port=args.port) 