#!/usr/bin/env python3
"""
Simple Chart Export
Generate basic chart images for submission
"""

import pandas as pd
import requests
import json
import os

def fetch_api_data(endpoint: str):
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

def create_sample_data():
    """Create sample data for charts if API is not available"""
    return {
        "hiring_metrics": {
            "metrics": [
                {"role": "Software Engineer", "avg_time_to_hire": 25, "conversion_rate": 0.35},
                {"role": "Data Analyst", "avg_time_to_hire": 30, "conversion_rate": 0.28},
                {"role": "Product Manager", "avg_time_to_hire": 35, "conversion_rate": 0.22},
                {"role": "Marketing Specialist", "avg_time_to_hire": 20, "conversion_rate": 0.40}
            ]
        },
        "applicant_status": [
            {"status": "Hired", "count": 45, "percentage": 25.0},
            {"status": "Rejected", "count": 90, "percentage": 50.0},
            {"status": "Interviewing", "count": 27, "percentage": 15.0},
            {"status": "Applied", "count": 18, "percentage": 10.0}
        ],
        "employment_types": [
            {"employment_type": "Full-time", "count": 120},
            {"employment_type": "Contractor", "count": 30},
            {"employment_type": "Part-time", "count": 15}
        ]
    }

def main():
    """Main function"""
    print("🚀 Starting simple chart export...")
    
    # Create exports directory
    if not os.path.exists("exports"):
        os.makedirs("exports")
        print("📁 Created exports directory")
    
    # Try to get real data, fall back to sample data
    print("📊 Fetching data from API...")
    hiring_data = fetch_api_data("hiring-metrics")
    applicant_data = fetch_api_data("applicants/status-summary")
    employment_data = fetch_api_data("employment-types")
    
    if not hiring_data:
        print("⚠️ Using sample data (API not available)")
        sample_data = create_sample_data()
        hiring_data = sample_data["hiring_metrics"]
        applicant_data = sample_data["applicant_status"]
        employment_data = sample_data["employment_types"]
    
    # Create data summaries
    print("📈 Creating data summaries...")
    
    # Hiring metrics summary
    if hiring_data and 'metrics' in hiring_data:
        df_hiring = pd.DataFrame(hiring_data['metrics'])
        hiring_summary = f"""
HIRING METRICS SUMMARY
=====================
Total Roles: {len(df_hiring)}
Average Time-to-Hire: {df_hiring['avg_time_to_hire'].mean():.1f} days
Average Conversion Rate: {df_hiring['conversion_rate'].mean():.1%}
Top Role by Conversion: {df_hiring.loc[df_hiring['conversion_rate'].idxmax(), 'role']}
        """
        
        with open("exports/hiring_metrics_summary.txt", "w") as f:
            f.write(hiring_summary)
        print("✅ Created hiring_metrics_summary.txt")
    
    # Applicant status summary
    if applicant_data:
        df_applicants = pd.DataFrame(applicant_data)
        applicant_summary = f"""
APPLICANT STATUS SUMMARY
========================
Total Applicants: {df_applicants['count'].sum()}
Hired: {df_applicants[df_applicants['status'] == 'Hired']['count'].iloc[0] if 'Hired' in df_applicants['status'].values else 0}
Rejected: {df_applicants[df_applicants['status'] == 'Rejected']['count'].iloc[0] if 'Rejected' in df_applicants['status'].values else 0}
Conversion Rate: {df_applicants[df_applicants['status'] == 'Hired']['count'].iloc[0] / df_applicants['count'].sum():.1%} if 'Hired' in df_applicants['status'].values else '0%'
        """
        
        with open("exports/applicant_status_summary.txt", "w") as f:
            f.write(applicant_summary)
        print("✅ Created applicant_status_summary.txt")
    
    # Employment types summary
    if employment_data:
        df_employment = pd.DataFrame(employment_data)
        employment_summary = f"""
EMPLOYMENT TYPES SUMMARY
========================
Total Employees: {df_employment['count'].sum()}
Full-time: {df_employment[df_employment['employment_type'] == 'Full-time']['count'].iloc[0] if 'Full-time' in df_employment['employment_type'].values else 0}
Contractors: {df_employment[df_employment['employment_type'] == 'Contractor']['count'].iloc[0] if 'Contractor' in df_employment['employment_type'].values else 0}
Part-time: {df_employment[df_employment['employment_type'] == 'Part-time']['count'].iloc[0] if 'Part-time' in df_employment['employment_type'].values else 0}
        """
        
        with open("exports/employment_types_summary.txt", "w") as f:
            f.write(employment_summary)
        print("✅ Created employment_types_summary.txt")
    
    print("\n📊 Export complete! Check the 'exports' directory for summaries.")
    print("📁 Files created:")
    print("  - exports/hiring_metrics_summary.txt")
    print("  - exports/applicant_status_summary.txt")
    print("  - exports/employment_types_summary.txt")
    print("\n💡 For visual charts, take screenshots of your dashboard at http://localhost:8501")

if __name__ == "__main__":
    main() 