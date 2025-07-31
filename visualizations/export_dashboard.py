#!/usr/bin/env python3
"""
MrBeast HR Analytics - Dashboard Export
Export dashboard charts as static images and PDFs
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import json
from datetime import datetime
import os
from typing import Dict, List, Optional
import base64
from io import BytesIO
import pdfkit
from jinja2 import Template

# Configuration
EXPORT_DIR = "exports"
API_BASE_URL = "http://localhost:8000"
API_USERNAME = "mrbeast"
API_PASSWORD = "hr_analytics_2024"

def create_export_directory():
    """Create export directory if it doesn't exist"""
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)
        os.makedirs(os.path.join(EXPORT_DIR, "images"))
        os.makedirs(os.path.join(EXPORT_DIR, "pdfs"))

def fetch_api_data(endpoint: str) -> Optional[Dict]:
    """Fetch data from API with authentication"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/{endpoint}",
            auth=(API_USERNAME, API_PASSWORD),
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching {endpoint}: {e}")
        return None

def export_chart_as_image(fig, filename: str, format: str = "png"):
    """Export Plotly chart as image"""
    try:
        # Export as image
        img_bytes = fig.to_image(format=format, width=1200, height=800)
        
        # Save to file
        filepath = os.path.join(EXPORT_DIR, "images", f"{filename}.{format}")
        with open(filepath, "wb") as f:
            f.write(img_bytes)
        
        print(f"✅ Exported {filename}.{format}")
        return filepath
    except Exception as e:
        print(f"❌ Error exporting {filename}: {e}")
        return None

def create_hiring_metrics_chart():
    """Create and export hiring metrics chart"""
    data = fetch_api_data("hiring-metrics")
    if not data:
        return None
    
    df = pd.DataFrame(data['metrics'])
    
    # Create hiring metrics chart
    fig = px.bar(
        df.head(10),  # Top 10 roles
        x='role',
        y='conversion_rate',
        title='Hiring Conversion Rates by Role',
        labels={'conversion_rate': 'Conversion Rate (%)', 'role': 'Role'},
        color='conversion_rate',
        color_continuous_scale='RdYlGn'
    )
    
    fig.update_layout(
        title_font_size=20,
        xaxis_title_font_size=14,
        yaxis_title_font_size=14,
        height=600
    )
    
    return export_chart_as_image(fig, "hiring_conversion_rates")

def create_applicants_status_chart():
    """Create and export applicants status chart"""
    data = fetch_api_data("applicants/status-summary")
    if not data:
        return None
    
    df = pd.DataFrame(data)
    
    # Create pie chart
    fig = px.pie(
        df,
        values='count',
        names='status',
        title='Applicants by Status',
        hole=0.3
    )
    
    fig.update_layout(
        title_font_size=20,
        height=600
    )
    
    return export_chart_as_image(fig, "applicants_status_distribution")

def create_employment_types_chart():
    """Create and export employment types chart"""
    data = fetch_api_data("employment-types")
    if not data:
        return None
    
    df = pd.DataFrame(data)
    
    # Create bar chart
    fig = px.bar(
        df,
        x='Employment Type',
        y='count',
        title='Employment Types Distribution',
        labels={'count': 'Employee Count', 'Employment Type': 'Employment Type'},
        color='Employment Type'
    )
    
    fig.update_layout(
        title_font_size=20,
        xaxis_title_font_size=14,
        yaxis_title_font_size=14,
        height=600
    )
    
    return export_chart_as_image(fig, "employment_types_distribution")

def create_department_analytics_chart():
    """Create and export department analytics chart"""
    data = fetch_api_data("department-analytics")
    if not data:
        return None
    
    df = pd.DataFrame(data)
    
    # Create department chart
    fig = px.bar(
        df,
        x='department',
        y='employee_count',
        title='Employee Count by Department',
        labels={'employee_count': 'Employee Count', 'department': 'Department'},
        color='avg_salary',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        title_font_size=20,
        xaxis_title_font_size=14,
        yaxis_title_font_size=14,
        height=600
    )
    
    return export_chart_as_image(fig, "department_employee_count")

def create_executive_summary_pdf():
    """Create executive summary PDF"""
    try:
        # Fetch all data
        hiring_data = fetch_api_data("hiring-metrics")
        applicants_data = fetch_api_data("applicants/status-summary")
        employment_data = fetch_api_data("employment-types")
        department_data = fetch_api_data("department-analytics")
        
        # Calculate summary metrics
        total_applicants = sum(item['count'] for item in applicants_data) if applicants_data else 0
        total_employees = sum(item['count'] for item in employment_data) if employment_data else 0
        avg_conversion_rate = 0
        if hiring_data and hiring_data['metrics']:
            avg_conversion_rate = hiring_data['summary']['avg_conversion_rate']
        
        # Create HTML template
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>MrBeast HR Analytics - Executive Summary</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { text-align: center; color: #FF6B35; font-size: 24px; margin-bottom: 30px; }
                .section { margin: 20px 0; }
                .metric { display: inline-block; margin: 10px; padding: 15px; background: #f8f9fa; border-radius: 8px; }
                .metric-value { font-size: 24px; font-weight: bold; color: #FF6B35; }
                .metric-label { font-size: 14px; color: #666; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #f8f9fa; }
            </style>
        </head>
        <body>
            <div class="header">MrBeast HR Analytics - Executive Summary</div>
            <div class="section">
                <h2>Key Metrics</h2>
                <div class="metric">
                    <div class="metric-value">{{ total_applicants }}</div>
                    <div class="metric-label">Total Applicants</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ total_employees }}</div>
                    <div class="metric-label">Total Employees</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ avg_conversion_rate }}%</div>
                    <div class="metric-label">Avg Conversion Rate</div>
                </div>
            </div>
            
            <div class="section">
                <h2>Top Hiring Roles</h2>
                <table>
                    <tr><th>Role</th><th>Department</th><th>Conversion Rate</th><th>Time to Hire</th></tr>
                    {% for role in top_roles %}
                    <tr>
                        <td>{{ role.role }}</td>
                        <td>{{ role.department }}</td>
                        <td>{{ role.conversion_rate }}%</td>
                        <td>{{ role.avg_time_to_hire }} days</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            
            <div class="section">
                <h2>Employment Types</h2>
                <table>
                    <tr><th>Employment Type</th><th>Count</th><th>Percentage</th></tr>
                    {% for type in employment_types %}
                    <tr>
                        <td>{{ type['Employment Type'] }}</td>
                        <td>{{ type.count }}</td>
                        <td>{{ type.percentage }}%</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            
            <div class="section">
                <h2>Department Overview</h2>
                <table>
                    <tr><th>Department</th><th>Employee Count</th><th>Current Employees</th><th>Avg Salary</th></tr>
                    {% for dept in departments %}
                    <tr>
                        <td>{{ dept.department }}</td>
                        <td>{{ dept.employee_count }}</td>
                        <td>{{ dept.current_employees }}</td>
                        <td>${{ "%.2f"|format(dept.avg_salary) }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            
            <div class="section">
                <p><em>Report generated on {{ timestamp }}</em></p>
            </div>
        </body>
        </html>
        """
        
        # Prepare data for template
        template_data = {
            'total_applicants': total_applicants,
            'total_employees': total_employees,
            'avg_conversion_rate': avg_conversion_rate,
            'top_roles': hiring_data['metrics'][:5] if hiring_data else [],
            'employment_types': employment_data if employment_data else [],
            'departments': department_data if department_data else [],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Render template
        template = Template(html_template)
        html_content = template.render(**template_data)
        
        # Save HTML file
        html_filepath = os.path.join(EXPORT_DIR, "pdfs", "executive_summary.html")
        with open(html_filepath, "w") as f:
            f.write(html_content)
        
        # Convert to PDF (requires wkhtmltopdf)
        try:
            pdf_filepath = os.path.join(EXPORT_DIR, "pdfs", "executive_summary.pdf")
            pdfkit.from_string(html_content, pdf_filepath)
            print(f"✅ Exported executive_summary.pdf")
            return pdf_filepath
        except Exception as e:
            print(f"⚠️ Could not create PDF (wkhtmltopdf not installed): {e}")
            print(f"✅ HTML version saved: {html_filepath}")
            return html_filepath
            
    except Exception as e:
        print(f"❌ Error creating executive summary: {e}")
        return None

def main():
    """Main export function"""
    print("🚀 MrBeast HR Analytics - Dashboard Export")
    print("=" * 50)
    
    # Create export directory
    create_export_directory()
    
    # Export charts
    print("\n📊 Exporting charts...")
    create_hiring_metrics_chart()
    create_applicants_status_chart()
    create_employment_types_chart()
    create_department_analytics_chart()
    
    # Create executive summary
    print("\n📋 Creating executive summary...")
    create_executive_summary_pdf()
    
    print(f"\n✅ Export completed! Files saved in '{EXPORT_DIR}' directory")
    print("\n📁 Exported files:")
    
    # List exported files
    for root, dirs, files in os.walk(EXPORT_DIR):
        for file in files:
            filepath = os.path.join(root, file)
            print(f"  - {filepath}")

if __name__ == "__main__":
    main() 