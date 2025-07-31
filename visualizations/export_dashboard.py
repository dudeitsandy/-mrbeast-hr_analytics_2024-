#!/usr/bin/env python3
"""
Export Dashboard Charts
Generate static images of key dashboard charts for submission
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

def fetch_api_data(endpoint: str) -> Optional[Dict]:
    """Fetch data from API"""
    try:
        response = requests.get(f"http://localhost:8000/{endpoint}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching {endpoint}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error connecting to API: {e}")
        return None

def export_hiring_metrics():
    """Export hiring metrics chart"""
    data = fetch_api_data("hiring-metrics")
    if not data or 'metrics' not in data:
        print("No hiring metrics data available")
        return
    
    df = pd.DataFrame(data['metrics'])
    
    # Create time-to-hire chart
    fig = px.bar(
        df, 
        x='role', 
        y='avg_time_to_hire',
        title="Average Time-to-Hire by Role",
        labels={'role': 'Role', 'avg_time_to_hire': 'Days to Hire'},
        color='conversion_rate',
        color_continuous_scale='RdYlGn'
    )
    
    fig.update_layout(
        width=800,
        height=500,
        title_x=0.5
    )
    
    fig.write_image("exports/hiring_metrics.png")
    print("✅ Exported hiring metrics chart")

def export_applicant_status():
    """Export applicant status chart"""
    data = fetch_api_data("applicants/status-summary")
    if not data:
        print("No applicant status data available")
        return
    
    df = pd.DataFrame(data)
    
    fig = px.pie(
        df,
        values='count',
        names='status',
        title="Applicant Status Distribution"
    )
    
    fig.update_layout(
        width=600,
        height=500,
        title_x=0.5
    )
    
    fig.write_image("exports/applicant_status.png")
    print("✅ Exported applicant status chart")

def export_employment_types():
    """Export employment types chart"""
    data = fetch_api_data("employment-types")
    if not data:
        print("No employment types data available")
        return
    
    df = pd.DataFrame(data)
    
    fig = px.bar(
        df,
        x='employment_type',
        y='count',
        title="Employment Type Distribution",
        labels={'employment_type': 'Employment Type', 'count': 'Count'}
    )
    
    fig.update_layout(
        width=600,
        height=500,
        title_x=0.5
    )
    
    fig.write_image("exports/employment_types.png")
    print("✅ Exported employment types chart")

def export_department_analytics():
    """Export department analytics chart"""
    data = fetch_api_data("department-analytics")
    if not data:
        print("No department analytics data available")
        return
    
    df = pd.DataFrame(data)
    
    fig = px.scatter(
        df,
        x='avg_salary',
        y='employee_count',
        size='avg_tenure',
        color='department',
        title="Department Analytics: Salary vs Employee Count",
        labels={'avg_salary': 'Average Salary', 'employee_count': 'Employee Count', 'avg_tenure': 'Avg Tenure'}
    )
    
    fig.update_layout(
        width=800,
        height=600,
        title_x=0.5
    )
    
    fig.write_image("exports/department_analytics.png")
    print("✅ Exported department analytics chart")

def create_export_directory():
    """Create exports directory if it doesn't exist"""
    if not os.path.exists("exports"):
        os.makedirs("exports")
        print("📁 Created exports directory")

def main():
    """Main export function"""
    print("🚀 Starting dashboard export...")
    
    # Create exports directory
    create_export_directory()
    
    # Export key charts
    export_hiring_metrics()
    export_applicant_status()
    export_employment_types()
    export_department_analytics()
    
    print("\n📊 Export complete! Check the 'exports' directory for static images.")
    print("📁 Files created:")
    print("  - exports/hiring_metrics.png")
    print("  - exports/applicant_status.png")
    print("  - exports/employment_types.png")
    print("  - exports/department_analytics.png")

if __name__ == "__main__":
    main() 