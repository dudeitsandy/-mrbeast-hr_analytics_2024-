#!/usr/bin/env python3
"""
MrBeast HR Analytics Dashboard
Focused dashboard for core HR analytics with meaningful metrics
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional, Tuple
import os
import base64

# Page configuration
st.set_page_config(
    page_title="MrBeast HR Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for MrBeast branding with improved contrast
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 2rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.2;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2E4057;
        margin: 2rem 0 1rem 0;
        border-bottom: 3px solid #FF6B35;
        padding-bottom: 0.5rem;
    }
    .insight-box {
        background-color: #f8f9fa;
        border-left: 4px solid #FF6B35;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
        color: #2E4057;
        font-weight: 500;
    }
    .metric-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .metric-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #2E4057;
        margin-bottom: 0.5rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.3;
    }
    .metric-value-large {
        font-size: 2rem;
        font-weight: bold;
        color: #FF6B35;
        margin: 0.5rem 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.1;
    }
    .metric-value-medium {
        font-size: 1.5rem;
        font-weight: bold;
        color: #667eea;
        margin: 0.5rem 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.2;
    }
    .metric-label-dark {
        font-size: 1rem;
        color: #2E4057;
        font-weight: 500;
        margin: 0.25rem 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .metric-subtitle {
        font-size: 1rem;
        color: #667eea;
        font-weight: 600;
        margin: 0.5rem 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .metric-description {
        font-size: 0.9rem;
        color: #6c757d;
        font-weight: 400;
        margin: 0.25rem 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .metric-card-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2E4057;
        margin-bottom: 0.75rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.2;
    }
    .metric-card-value {
        font-size: 2.2rem;
        font-weight: bold;
        color: #FF6B35;
        margin: 0.5rem 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.1;
    }
    .metric-card-label {
        font-size: 1rem;
        color: #2E4057;
        font-weight: 500;
        margin: 0.25rem 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .metric-card-subtitle {
        font-size: 1rem;
        color: #667eea;
        font-weight: 600;
        margin: 0.5rem 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 2rem;
    }
    .logo-container img {
        max-width: 200px;
        height: auto;
    }
    .filter-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
    }
    .filter-title {
        font-size: 1.1rem;
        font-weight: bold;
        color: #2E4057;
        margin-bottom: 0.5rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .section-subtitle {
        font-size: 1rem;
        color: #6c757d;
        font-weight: 400;
        margin: 0.5rem 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.4;
    }
    .insight-text {
        font-size: 0.95rem;
        color: #2E4057;
        font-weight: 500;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.5;
    }
    .chart-title {
        font-size: 1.4rem;
        font-weight: bold;
        color: #2E4057;
        margin: 1rem 0 0.5rem 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.3;
    }
    }
</style>
""", unsafe_allow_html=True)

def get_logo_base64():
    """Get MrBeast logo as base64 string"""
    try:
        logo_path = "assets/mrbeast-logo.png"
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                logo_bytes = f.read()
                logo_base64 = base64.b64encode(logo_bytes).decode()
                return f"data:image/png;base64,{logo_base64}"
        else:
            # Fallback to a simple text logo if file doesn't exist
            return None
    except:
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_api_data(endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
    """Fetch data from API with enhanced error handling"""
    try:
        response = requests.get(f"http://localhost:8000/{endpoint}", params=params, timeout=15)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            st.warning(f"Endpoint '{endpoint}' not found. This feature may not be available.")
            return None
        elif response.status_code == 500:
            st.error(f"Server error for endpoint '{endpoint}'. The API may be experiencing issues.")
            return None
        else:
            st.error(f"API Error {response.status_code} for endpoint '{endpoint}': {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Cannot connect to API server. Please ensure the API is running on http://localhost:8000")
        return None
    except requests.exceptions.Timeout:
        st.error(f"⏱️ Request timeout for endpoint '{endpoint}'. The API may be slow or unresponsive.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"🌐 Network error for endpoint '{endpoint}': {e}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error fetching data from '{endpoint}': {e}")
        return None

def check_api_health() -> bool:
    """Check if API is available"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def calculate_core_kpis(hiring_metrics: List[Dict], status_summary: Dict = None, filters: Dict = None) -> Tuple[int, float, float, int, float]:
    """Calculate core KPIs from hiring metrics with optional filtering"""
    if not hiring_metrics:
        return 0, 0.0, 0.0, 0, 0.0
    
    # Apply filters if provided
    filtered_metrics = hiring_metrics
    if filters:
        if filters.get('role') and filters['role'] != 'All':
            filtered_metrics = [m for m in hiring_metrics if m.get('role') == filters['role']]
        if filters.get('department') and filters['department'] != 'All':
            filtered_metrics = [m for m in filtered_metrics if m.get('department') == filters['department']]
    
    if not filtered_metrics:
        return 0, 0.0, 0.0, 0, 0.0
    
    total_applicants = sum(metric.get('total_applicants', 0) for metric in filtered_metrics)
    total_hired = sum(metric.get('hired_count', 0) for metric in filtered_metrics)
    total_rejected = sum(metric.get('rejected_count', 0) for metric in filtered_metrics)
    
    # Calculate conversion rate (hired / total applicants)
    conversion_rate = (total_hired / total_applicants * 100) if total_applicants > 0 else 0
    
    # Calculate average time to hire - fix the calculation
    total_time_to_hire = 0
    total_hired_with_time = 0
    
    for metric in filtered_metrics:
        time_to_hire = metric.get('avg_time_to_hire', 0)  # Fixed column name
        hired_count = metric.get('hired_count', 0)
        if time_to_hire > 0 and hired_count > 0:
            total_time_to_hire += time_to_hire * hired_count
            total_hired_with_time += hired_count
    
    avg_time_to_hire = total_time_to_hire / total_hired_with_time if total_hired_with_time > 0 else 0
    
    # Calculate in-flight candidates (not hired or rejected)
    completed_applications = total_hired + total_rejected
    in_flight_candidates = total_applicants - completed_applications
    
    return total_applicants, conversion_rate, avg_time_to_hire, in_flight_candidates, completed_applications

def create_core_kpi_cards(total_applicants: int, conversion_rate: float, avg_time_to_hire: float, in_flight_candidates: int, completed_applications: int):
    """Create core KPI cards"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="kpi-card">
            <div class="metric-label">Total Applicants</div>
            <div class="metric-value">{}</div>
        </div>
        """.format(f"{total_applicants:,}"), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="kpi-card">
            <div class="metric-label">Conversion Rate</div>
            <div class="metric-value">{:.1f}%</div>
        </div>
        """.format(conversion_rate), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="kpi-card">
            <div class="metric-label">Avg Time to Hire</div>
            <div class="metric-value">{:.0f} days</div>
        </div>
        """.format(avg_time_to_hire), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="kpi-card">
            <div class="metric-label">In Pipeline</div>
            <div class="metric-value">{}</div>
        </div>
        """.format(f"{in_flight_candidates:,}"), unsafe_allow_html=True)

def create_hiring_metrics_chart(hiring_metrics: List[Dict], filters: Dict = None):
    """Create hiring metrics chart with conversion rate and time-to-hire analysis"""
    if not hiring_metrics:
        st.warning("No hiring metrics data available")
        return
    
    df = pd.DataFrame(hiring_metrics)
    
    # Apply filters if provided
    if filters:
        if filters.get('role') and filters['role'] != 'All':
            df = df[df['role'] == filters['role']]
        if filters.get('department') and filters['department'] != 'All':
            df = df[df['department'] == filters['department']]
    
    if df.empty:
        st.info("No data available for selected filters")
        return
    
    # Sort by total applicants
    df = df.sort_values('total_applicants', ascending=True)
    
    # Calculate conversion rates for labels
    df['conversion_rate'] = (df['hired_count'] / df['total_applicants'] * 100).fillna(0)
    
    # Create two columns for conversion rate and time-to-hire
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Conversion Rate Analysis")
        fig_conversion = go.Figure()
        
        # Add bars for applicants and hired
        fig_conversion.add_trace(go.Bar(
            y=df['role'],
            x=df['total_applicants'],
            name='Total Applicants',
            marker_color='#667eea',
            orientation='h',
            text=df['total_applicants'],
            textposition='auto'
        ))
        
        fig_conversion.add_trace(go.Bar(
            y=df['role'],
            x=df['hired_count'],
            name='Hired',
            marker_color='#FF6B35',
            orientation='h',
            text=[f"{rate:.1f}%" for rate in df['conversion_rate']],
            textposition='auto'
        ))
        
        fig_conversion.update_layout(
            title="Hiring Conversion Rate by Role",
            xaxis_title="Number of Candidates",
            yaxis_title="Role",
            barmode='group',
            height=400
        )
        
        st.plotly_chart(fig_conversion, use_container_width=True)
        
        # Add conversion rate insights
        add_chart_insights(df, "conversion_rate")
    
    with col2:
        st.markdown("### Time-to-Hire Analysis")
        
        # Filter out roles with no time-to-hire data
        df_time = df[df['avg_time_to_hire'] > 0].copy()  # Fixed column name
        
        if not df_time.empty:
            fig_time = go.Figure()
            
            fig_time.add_trace(go.Bar(
                y=df_time['role'],
                x=df_time['avg_time_to_hire'],  # Fixed column name
                name='Avg Time to Hire',
                marker_color='#28a745',
                orientation='h',
                text=[f"{days:.0f} days" for days in df_time['avg_time_to_hire']],  # Fixed column name
                textposition='auto'
            ))
            
            fig_time.update_layout(
                title="Average Time to Hire by Role",
                xaxis_title="Days",
                yaxis_title="Role",
                height=400
            )
            
            st.plotly_chart(fig_time, use_container_width=True)
            
            # Add time-to-hire insights
            add_time_to_hire_insights(df_time)
        else:
            st.info("No time-to-hire data available")

def add_time_to_hire_insights(df: pd.DataFrame):
    """Add insights for time-to-hire analysis"""
    if df.empty:
        return
    
    # Find roles with fastest and slowest hiring
    fastest_role = df.loc[df['avg_time_to_hire'].idxmin()]  # Fixed column name
    slowest_role = df.loc[df['avg_time_to_hire'].idxmax()]  # Fixed column name
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="insight-box">
            <strong>⚡ Fastest Hiring:</strong><br>
            {fastest_role['role']} - {fastest_role['avg_time_to_hire']:.0f} days
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="insight-box">
            <strong>🐌 Slowest Hiring:</strong><br>
            {slowest_role['role']} - {slowest_role['avg_time_to_hire']:.0f} days
        </div>
        """, unsafe_allow_html=True)

def create_pipeline_visualization(filters: Dict = None):
    """Create pipeline visualization by stage with optional filtering"""
    hiring_metrics = fetch_api_data("hiring-metrics")
    
    if not hiring_metrics or not hiring_metrics.get('metrics'):
        st.warning("No hiring metrics data available")
        return
    
    st.markdown('<h3 class="section-header">Pipeline Analysis</h3>', unsafe_allow_html=True)
    
    # Apply filters if provided
    metrics = hiring_metrics['metrics']
    if filters:
        if filters.get('role') and filters['role'] != 'All':
            metrics = [m for m in metrics if m.get('role') == filters['role']]
        if filters.get('department') and filters['department'] != 'All':
            metrics = [m for m in metrics if m.get('department') == filters['department']]
    
    if not metrics:
        st.info("No data available for selected filters")
        return
    
    # Calculate pipeline stages (excluding hired and rejected)
    pipeline_data = []
    
    for metric in metrics:
        role = metric.get('role', 'Unknown')
        total = metric.get('total_applicants', 0)
        hired = metric.get('hired_count', 0)
        rejected = metric.get('rejected_count', 0)
        interviewing = metric.get('interviewing_count', 0)
        
        # Calculate pipeline stages
        in_pipeline = total - hired - rejected
        applied = in_pipeline - interviewing
        
        pipeline_data.append({
            'role': role,
            'applied': applied,
            'interviewing': interviewing,
            'in_pipeline': in_pipeline
        })
    
    df_pipeline = pd.DataFrame(pipeline_data)
    
    if not df_pipeline.empty:
        # Sort by total pipeline
        df_pipeline['total_pipeline'] = df_pipeline['in_pipeline']
        df_pipeline = df_pipeline.sort_values('total_pipeline', ascending=True)
        
        fig = go.Figure()
        
        # Add bars for each pipeline stage
        fig.add_trace(go.Bar(
            y=df_pipeline['role'],
            x=df_pipeline['applied'],
            name='Applied',
            marker_color='#6c757d',
            orientation='h'
        ))
        
        fig.add_trace(go.Bar(
            y=df_pipeline['role'],
            x=df_pipeline['interviewing'],
            name='Interviewing',
            marker_color='#ffc107',
            orientation='h'
        ))
        
        fig.update_layout(
            title="Pipeline Stages by Role (Excluding Hired/Rejected)",
            xaxis_title="Number of Candidates",
            yaxis_title="Role",
            barmode='stack',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add pipeline insights
        add_pipeline_insights(df_pipeline)

def add_chart_insights(df: pd.DataFrame, chart_type: str):
    """Add insights based on chart data"""
    if df.empty:
        return
    
    if chart_type == "conversion_rate":
        # Find roles with highest and lowest conversion rates
        df['conversion_rate'] = (df['hired_count'] / df['total_applicants'] * 100).fillna(0)
        
        best_role = df.loc[df['conversion_rate'].idxmax()]
        worst_role = df.loc[df['conversion_rate'].idxmin()]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="insight-box">
                <strong>🎯 Best Performing Role:</strong><br>
                {best_role['role']} - {best_role['conversion_rate']:.1f}% conversion rate
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="insight-box">
                <strong>⚠️ Needs Attention:</strong><br>
                {worst_role['role']} - {worst_role['conversion_rate']:.1f}% conversion rate
            </div>
            """, unsafe_allow_html=True)

def add_pipeline_insights(df: pd.DataFrame):
    """Add insights for pipeline analysis"""
    if df.empty:
        return
    
    # Find roles with largest and smallest pipelines
    largest_pipeline = df.loc[df['in_pipeline'].idxmax()]
    smallest_pipeline = df.loc[df['in_pipeline'].idxmin()]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="insight-box">
            <strong>📊 Largest Pipeline:</strong><br>
            {largest_pipeline['role']} - {largest_pipeline['in_pipeline']} candidates
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="insight-box">
            <strong>📉 Smallest Pipeline:</strong><br>
            {smallest_pipeline['role']} - {smallest_pipeline['in_pipeline']} candidates
        </div>
        """, unsafe_allow_html=True)

def create_employment_type_analysis(filters: Dict = None):
    """Create employment type analysis with improved contrast"""
    employment_data = fetch_api_data("employment-types")
    
    if not employment_data:
        st.warning("Unable to fetch employment type data")
        return
    
    st.markdown('<h3 class="section-header">Employment Type Distribution</h3>', unsafe_allow_html=True)
    
    # Create employment type chart
    # Handle both list and dict responses from API
    if isinstance(employment_data, list):
        df = pd.DataFrame(employment_data)
    else:
        df = pd.DataFrame(employment_data.get('employment_types', []))
    
    # Apply filters if provided
    if filters and filters.get('employee_type') and filters['employee_type'] != 'All':
        # Note: Employment type data doesn't have role/department filters, so we'll show all
        pass
    
    if not df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Map API column names to expected names
            if 'Employment Type' in df.columns:
                df = df.rename(columns={
                    'Employment Type': 'employment_type',
                    'count': 'employee_count',
                    'percentage': 'percentage'
                })
            
            fig = px.pie(df, 
                        values='employee_count', 
                        names='employment_type',
                        title="Employment Type Distribution",
                        color_discrete_map={'Full-time': '#FF6B35', 'Contractor': '#667eea'})
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            for _, row in df.iterrows():
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">{row['employment_type']}</div>
                    <div class="metric-value-large">{row['employee_count']}</div>
                    <div class="metric-label-dark">Employees</div>
                    <div class="metric-subtitle">{row.get('percentage', 0):.1f}%</div>
                    <div class="metric-label-dark">Percentage</div>
                </div>
                """, unsafe_allow_html=True)

def create_salary_analysis(filters: Dict = None):
    """Create salary analysis by role and department with currency formatting"""
    employee_data = fetch_api_data("master-employee-view")
    
    if not employee_data:
        st.warning("Unable to fetch employee data")
        return
    
    st.markdown('<h3 class="section-header">Salary Analysis</h3>', unsafe_allow_html=True)
    
    # Add analysis type selector
    analysis_type = st.selectbox(
        "Select Salary Analysis Type:",
        ["By Department", "By Role", "By Role and Department"],
        help="Choose how to analyze salary data"
    )
    
    # Handle both list and dict responses from API
    if isinstance(employee_data, list):
        df = pd.DataFrame(employee_data)
    else:
        df = pd.DataFrame(employee_data.get('employees', []))
    
    if not df.empty:
        # Apply filters
        if filters:
            if filters.get('role') and filters['role'] != 'All':
                # Use applied_role column if it exists, otherwise use role
                if 'applied_role' in df.columns:
                    df = df[df['applied_role'] == filters['role']]
                elif 'role' in df.columns:
                    df = df[df['role'] == filters['role']]
            if filters.get('department') and filters['department'] != 'All':
                df = df[df['Department'] == filters['department']]
            if filters.get('employee_type') and filters['employee_type'] != 'All':
                df = df[df['Employment Type'] == filters['employee_type']]
        
        if analysis_type == "By Department":
            # Salary by department
            dept_salary = df.groupby('Department')['Salary'].agg(['mean', 'count']).reset_index()
            dept_salary.columns = ['Department', 'Average Salary', 'Employee Count']
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(dept_salary, 
                            x='Department', 
                            y='Average Salary',
                            title="Average Salary by Department",
                            color='Average Salary',
                            color_continuous_scale='viridis',
                            text=dept_salary['Average Salary'].apply(lambda x: f"${x:,.0f}"))
                
                fig.update_traces(textposition='auto')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Display salary statistics
                st.markdown("### Salary Statistics by Department")
                for _, row in dept_salary.iterrows():
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">{row['Department']}</div>
                        <div class="metric-value-large">${row['Average Salary']:,.0f}</div>
                        <div class="metric-label-dark">Avg Salary ({row['Employee Count']} employees)</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        elif analysis_type == "By Role":
            # Salary by role - use applied_role if available, otherwise use role
            role_column = 'applied_role' if 'applied_role' in df.columns else 'role'
            if role_column in df.columns:
                role_salary = df.groupby(role_column)['Salary'].agg(['mean', 'count']).reset_index()
                role_salary.columns = ['Role', 'Average Salary', 'Employee Count']
                role_salary = role_salary.sort_values('Average Salary', ascending=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.bar(role_salary, 
                                x='Role', 
                                y='Average Salary',
                                title="Average Salary by Role",
                                color='Average Salary',
                                color_continuous_scale='viridis',
                                text=role_salary['Average Salary'].apply(lambda x: f"${x:,.0f}"))
                    
                    fig.update_traces(textposition='auto')
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Display salary statistics
                    st.markdown("### Salary Statistics by Role")
                    for _, row in role_salary.iterrows():
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-title">{row['Role']}</div>
                            <div class="metric-value-large">${row['Average Salary']:,.0f}</div>
                            <div class="metric-label-dark">Avg Salary ({row['Employee Count']} employees)</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No role information available in employee data")
        
        elif analysis_type == "By Role and Department":
            # Salary by role and department
            role_column = 'applied_role' if 'applied_role' in df.columns else 'role'
            if role_column in df.columns:
                role_dept_salary = df.groupby([role_column, 'Department'])['Salary'].agg(['mean', 'count']).reset_index()
                role_dept_salary.columns = ['Role', 'Department', 'Average Salary', 'Employee Count']
                role_dept_salary = role_dept_salary.sort_values('Average Salary', ascending=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.bar(role_dept_salary, 
                                x='Role', 
                                y='Average Salary',
                                color='Department',
                                title="Average Salary by Role and Department",
                                text=role_dept_salary['Average Salary'].apply(lambda x: f"${x:,.0f}"))
                    
                    fig.update_traces(textposition='auto')
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Display salary statistics
                    st.markdown("### Salary Statistics by Role and Department")
                    for _, row in role_dept_salary.iterrows():
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-title">{row['Role']} - {row['Department']}</div>
                            <div class="metric-value-large">${row['Average Salary']:,.0f}</div>
                            <div class="metric-label-dark">Avg Salary ({row['Employee Count']} employees)</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No role information available in employee data")

def create_tenure_analysis(filters: Dict = None):
    """Create tenure analysis by role and department"""
    st.markdown('<h3 class="section-header">Tenure Analysis by Role and Department</h3>', unsafe_allow_html=True)
    
    try:
        employee_data = fetch_api_data("master-employee-view")
        
        if not employee_data or not employee_data.get('employees'):
            st.warning("No employee data available for tenure analysis")
            return
        
        employees = employee_data['employees']
        
        # Apply filters
        if filters:
            if filters.get('role') and filters['role'] != 'All':
                employees = [e for e in employees if e.get('applied_role') == filters['role']]
            if filters.get('department') and filters['department'] != 'All':
                employees = [e for e in employees if e.get('Department') == filters['department']]
            if filters.get('employee_type') and filters['employee_type'] != 'All':
                employees = [e for e in employees if e.get('Employment Type') == filters['employee_type']]
        
        if not employees:
            st.info("No employees found with the selected filters")
            return
        
        # Create DataFrame for analysis
        df = pd.DataFrame(employees)
        
        # Calculate tenure for current employees
        current_employees = df[df['employment_status'] == 'Current'].copy()
        
        if current_employees.empty:
            st.warning("No current employees found in filtered data")
            return
        
        # Calculate tenure in days with data quality checks
        current_employees['start_date'] = pd.to_datetime(current_employees['Start Date'], errors='coerce')
        
        # Filter out employees with invalid start dates
        valid_employees = current_employees.dropna(subset=['start_date'])
        
        if valid_employees.empty:
            st.warning("No employees with valid start dates found")
            return
        
        # Calculate tenure and filter out negative or unreasonable values
        valid_employees['tenure_days'] = (pd.Timestamp.now() - valid_employees['start_date']).dt.days
        
        # Quality check: filter out negative tenures and unreasonable values (> 50 years)
        quality_employees = valid_employees[
            (valid_employees['tenure_days'] >= 0) & 
            (valid_employees['tenure_days'] <= 18250)  # 50 years max
        ].copy()
        
        if quality_employees.empty:
            st.warning("No employees with valid tenure data found after quality checks")
            return
        
        # Show data quality summary
        total_employees = len(current_employees)
        valid_tenure_employees = len(quality_employees)
        invalid_employees = total_employees - valid_tenure_employees
        
        if invalid_employees > 0:
            st.info(f"📊 Data Quality: {valid_tenure_employees}/{total_employees} employees have valid tenure data ({invalid_employees} excluded due to invalid dates or negative tenures)")
        
        # Group by role and department
        role_dept_tenure = quality_employees.groupby(['applied_role', 'Department'])['tenure_days'].agg(['count', 'mean', 'min', 'max']).round(1)
        role_dept_tenure.columns = ['Employee_Count', 'Avg_Tenure_Days', 'Min_Tenure_Days', 'Max_Tenure_Days']
        
        if role_dept_tenure.empty:
            st.warning("No tenure data available after grouping by role and department")
            return
        
        # Create two columns for different visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Average Tenure by Role and Department")
            
            # Create bar chart for average tenure
            fig_avg = px.bar(
                role_dept_tenure.reset_index(),
                x='applied_role',
                y='Avg_Tenure_Days',
                color='Department',
                title='Average Tenure by Role and Department',
                labels={'applied_role': 'Role', 'Avg_Tenure_Days': 'Average Tenure (Days)', 'Department': 'Department'},
                barmode='group'
            )
            fig_avg.update_layout(height=400)
            st.plotly_chart(fig_avg, use_container_width=True)
        
        with col2:
            st.markdown("### Tenure Distribution by Department")
            
            # Create box plot for tenure distribution
            fig_dist = px.box(
                quality_employees,
                x='Department',
                y='tenure_days',
                title='Tenure Distribution by Department',
                labels={'Department': 'Department', 'tenure_days': 'Tenure (Days)'}
            )
            fig_dist.update_layout(height=400)
            st.plotly_chart(fig_dist, use_container_width=True)
        
        # Create a more compact display with better formatting
        tenure_stats = role_dept_tenure.reset_index()
        tenure_stats['Avg_Tenure_Years'] = (tenure_stats['Avg_Tenure_Days'] / 365.25).round(1)
        tenure_stats['Min_Tenure_Years'] = (tenure_stats['Min_Tenure_Days'] / 365.25).round(1)
        tenure_stats['Max_Tenure_Years'] = (tenure_stats['Max_Tenure_Days'] / 365.25).round(1)
        
        # Show longest and shortest average tenure metrics
        st.markdown("### 📊 Tenure Highlights")
        
        # Calculate longest and shortest average tenure by role and department
        if not tenure_stats.empty:
            # Filter out any tenure data with 0 or negative values to ensure shortest is greater than 0
            valid_tenure_stats = tenure_stats[tenure_stats['Avg_Tenure_Years'] > 0].copy()
            
            if not valid_tenure_stats.empty:
                # Longest average tenure by role
                longest_role = valid_tenure_stats.loc[valid_tenure_stats['Avg_Tenure_Years'].idxmax()]
                
                # Longest average tenure by department
                dept_tenure = valid_tenure_stats.groupby('Department')['Avg_Tenure_Years'].mean()
                longest_dept_name = dept_tenure.idxmax()
                longest_dept_avg = dept_tenure.max()
                
                # Shortest average tenure by role (now guaranteed to be > 0)
                shortest_role = valid_tenure_stats.loc[valid_tenure_stats['Avg_Tenure_Years'].idxmin()]
                
                # Shortest average tenure by department
                shortest_dept_name = dept_tenure.idxmin()
                shortest_dept_avg = dept_tenure.min()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">Longest Average Tenure by Role</div>
                        <div class="metric-value-large">{longest_role['applied_role'] if pd.notna(longest_role['applied_role']) else 'Unknown'}</div>
                        <div class="metric-label-dark">{longest_role['Avg_Tenure_Years']:.1f} years</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">Longest Average Tenure by Department</div>
                        <div class="metric-value-large">{longest_dept_name if pd.notna(longest_dept_name) else 'Unknown'}</div>
                        <div class="metric-label-dark">{longest_dept_avg:.1f} years</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">Shortest Average Tenure by Role</div>
                        <div class="metric-value-large">{shortest_role['applied_role'] if pd.notna(shortest_role['applied_role']) else 'Unknown'}</div>
                        <div class="metric-label-dark">{shortest_role['Avg_Tenure_Years']:.1f} years</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">Shortest Average Tenure by Department</div>
                        <div class="metric-value-large">{shortest_dept_name if pd.notna(shortest_dept_name) else 'Unknown'}</div>
                        <div class="metric-label-dark">{shortest_dept_avg:.1f} years</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No valid tenure data available (all average tenures are 0 or negative)")
        
        # Show detailed tenure statistics
        st.markdown("### 📊 Detailed Tenure Statistics")
        
        # Display as a table with better formatting
        display_stats = tenure_stats[['applied_role', 'Department', 'Employee_Count', 'Avg_Tenure_Years', 'Min_Tenure_Years', 'Max_Tenure_Years']].rename(columns={
            'applied_role': 'Role',
            'Department': 'Department',
            'Employee_Count': 'Employees',
            'Avg_Tenure_Years': 'Avg (Years)',
            'Min_Tenure_Years': 'Min (Years)',
            'Max_Tenure_Years': 'Max (Years)'
        })
        
        st.dataframe(display_stats, use_container_width=True)
        
        # Add tenure insights
        add_tenure_insights(tenure_stats)
        
    except Exception as e:
        st.error(f"Error in tenure analysis: {str(e)}")
        st.info("Please check if the API is running and data is available")

def add_tenure_insights(tenure_stats: pd.DataFrame):
    """Add insights for tenure analysis"""
    if tenure_stats.empty:
        return
    
    # Filter out any tenure data with 0 or negative values to ensure shortest is greater than 0
    valid_tenure_stats = tenure_stats[tenure_stats['Avg_Tenure_Years'] > 0].copy()
    
    if valid_tenure_stats.empty:
        st.info("No valid tenure data available for insights (all average tenures are 0 or negative)")
        return
    
    # Find roles with highest and lowest average tenure
    highest_tenure = valid_tenure_stats.loc[valid_tenure_stats['Avg_Tenure_Days'].idxmax()]
    lowest_tenure = valid_tenure_stats.loc[valid_tenure_stats['Avg_Tenure_Days'].idxmin()]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="insight-box">
            <strong>🏆 Longest Average Tenure:</strong><br>
            {highest_tenure['applied_role']} - {highest_tenure['Department']}<br>
            {highest_tenure['Avg_Tenure_Years']} years ({highest_tenure['Employee_Count']} employees)
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="insight-box">
            <strong>🆕 Shortest Average Tenure:</strong><br>
            {lowest_tenure['applied_role']} - {lowest_tenure['Department']}<br>
            {lowest_tenure['Avg_Tenure_Years']} years ({lowest_tenure['Employee_Count']} employees)
        </div>
        """, unsafe_allow_html=True)

def add_hiring_success_insights(success_df: pd.DataFrame):
    """Add insights for hiring success analysis"""
    if success_df.empty:
        return
    
    # Find best and worst performing application statuses
    best_status = success_df.loc[success_df['conversion_to_employee_rate'].idxmax()]
    worst_status = success_df.loc[success_df['conversion_to_employee_rate'].idxmin()]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="insight-box">
            <strong>🎯 Best Conversion Rate:</strong><br>
            {best_status['application_status']}<br>
            {best_status['conversion_to_employee_rate']:.1f}% ({best_status['employee_matches']}/{best_status['applicant_count']})
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="insight-box">
            <strong>⚠️ Lowest Conversion Rate:</strong><br>
            {worst_status['application_status']}<br>
            {worst_status['conversion_to_employee_rate']:.1f}% ({worst_status['employee_matches']}/{worst_status['applicant_count']})
        </div>
        """, unsafe_allow_html=True)

def create_data_quality_analysis():
    """Create data quality analysis showing the realistic HR data scenario"""
    st.markdown('<h3 class="section-header">Data Quality Analysis</h3>', unsafe_allow_html=True)
    
    # Fetch data quality information with better error handling
    data_quality = fetch_api_data("data-quality-analysis")
    hiring_success = fetch_api_data("hiring-success-analysis")
    employee_source = fetch_api_data("employee-source-analysis")
    
    # Check if we have any data to work with
    has_data_quality = data_quality and data_quality.get('analysis')
    has_hiring_success = hiring_success and hiring_success.get('analysis')
    has_employee_source = employee_source and employee_source.get('analysis')
    
    if not any([has_data_quality, has_hiring_success, has_employee_source]):
        st.warning("⚠️ No data quality analysis available. This may indicate:")
        st.markdown("""
        - Database views may not be created yet
        - API endpoints may be experiencing issues
        - Data pipeline may need to be run
        
        **To fix this:**
        1. Run the database setup: `.\scripts\\run_pipeline.ps1`
        2. Restart the API server: `.\api\\run_api.ps1`
        3. Refresh this dashboard
        """)
        return
    
    if has_data_quality:
        analysis = data_quality['analysis']
        
        # Create summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            applicants_data = next((a for a in analysis if a['data_source'] == 'Applicants'), {})
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Applicants</div>
                <div class="metric-value-large">{applicants_data.get('total_records', 0)}</div>
                <div class="metric-label-dark">Application Records</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            employees_data = next((a for a in analysis if a['data_source'] == 'Employees'), {})
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Employees</div>
                <div class="metric-value-large">{employees_data.get('total_records', 0)}</div>
                <div class="metric-label-dark">Employee Records</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            hired_count = applicants_data.get('hired_count', 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Hired Applicants</div>
                <div class="metric-value-large">{hired_count}</div>
                <div class="metric-label-dark">Successfully Hired</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            conversion_rate = round((hired_count / applicants_data.get('total_records', 1)) * 100, 1) if applicants_data.get('total_records', 0) > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Hiring Rate</div>
                <div class="metric-value-large">{conversion_rate}%</div>
                <div class="metric-label-dark">Applicants to Employees</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Show employee source analysis
        if has_employee_source:
            st.markdown("### 👥 Employee Source Analysis")
            
            try:
                source_df = pd.DataFrame(employee_source['analysis'])
                if not source_df.empty:
                    fig = px.pie(
                        source_df,
                        values='employee_count',
                        names='employee_source',
                        title='Employee Source Distribution',
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show insights
                    st.markdown("#### 💡 Key Insights")
                    for _, row in source_df.iterrows():
                        source_type = row['employee_source'].replace('_', ' ').title()
                        percentage = row['percentage_of_total_employees']
                        count = row['employee_count']
                        
                        if 'Application Process' in source_type:
                            st.info(f"📝 **{percentage}%** of employees ({count} people) came through the application process")
                        else:
                            st.warning(f"🎯 **{percentage}%** of employees ({count} people) were direct hires or transfers")
            except Exception as e:
                st.error(f"Error displaying employee source analysis: {str(e)}")
                st.info("Please check the data format and try again")
        else:
            st.info("No employee source analysis data available")
    
    # Show data quality warnings
    st.markdown("### ⚠️ Data Quality Notes")
    st.markdown("""
    **Realistic HR Scenario Detected:**
    - Not all applicants become employees (realistic hiring funnel)
    - Not all employees came through the application process (direct hires, transfers, etc.)
    - Role-department mapping only works for employees who applied and were hired
    - This is a **realistic** data scenario, not a data quality issue
    """)

def create_role_validation_analysis():
    """Create role-department validation analysis"""
    st.markdown('<h3 class="section-header">Role-Department Mapping Validation</h3>', unsafe_allow_html=True)
    
    validation_data = fetch_api_data("role-department-validation")
    
    if validation_data and validation_data.get('validations'):
        validations = validation_data['validations']
        summary = validation_data.get('summary', {})
        
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Mappings</div>
                <div class="metric-value-large">{summary.get('total_mappings', 0)}</div>
                <div class="metric-label-dark">Role-Department Pairs</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Validated</div>
                <div class="metric-value-large">{summary.get('validated_mappings', 0)}</div>
                <div class="metric-label-dark">Confirmed Mappings</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Valid</div>
                <div class="metric-value-large">{summary.get('valid_mappings', 0)}</div>
                <div class="metric-label-dark">One-to-One Mappings</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            validation_rate = summary.get('validation_rate', 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Validation Rate</div>
                <div class="metric-value-large">{validation_rate}%</div>
                <div class="metric-label-dark">Data Quality Score</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Display validation details
        st.markdown("### Role-Department Mapping Details")
        
        # Create DataFrame for better display
        df = pd.DataFrame(validations)
        
        if not df.empty:
            # Display as styled table
            st.dataframe(
                df[['role', 'department', 'mapping_validation', 'employee_count', 'application_count', 'confidence_score']].rename(columns={
                    'role': 'Role',
                    'department': 'Department', 
                    'mapping_validation': 'Validation',
                    'employee_count': 'Employees',
                    'application_count': 'Applications',
                    'confidence_score': 'Confidence'
                }),
                use_container_width=True
            )
            
            # Show conflicts if any
            conflicts = df[df['mapping_validation'] != 'VALID']
            if not conflicts.empty:
                st.warning(f"⚠️ Found {len(conflicts)} role-department mapping conflicts that need attention")
                
                for _, conflict in conflicts.iterrows():
                    st.markdown(f"""
                    **{conflict['role']}** -> **{conflict['department']}** ({conflict['mapping_validation']})
                    - {conflict['employee_count']} employees, {conflict['application_count']} applications
                    """)
        else:
            st.info("No role-department mappings found")
    else:
        st.warning("No role-department validation data available")

def create_additional_metrics(filters: Dict = None):
    """Create additional meaningful metrics"""
    
    # Fetch various data sources
    hiring_metrics = fetch_api_data("hiring-metrics")
    employee_data = fetch_api_data("master-employee-view")
    department_data = fetch_api_data("department-analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if hiring_metrics and hiring_metrics.get('metrics'):
            metrics = hiring_metrics['metrics']
            
            # Apply filters if provided
            if filters:
                if filters.get('role') and filters['role'] != 'All':
                    metrics = [m for m in metrics if m.get('role') == filters['role']]
                if filters.get('department') and filters['department'] != 'All':
                    metrics = [m for m in metrics if m.get('department') == filters['department']]
            
            if metrics:
                # Most in-demand role
                most_demand = max(metrics, key=lambda x: x.get('total_applicants', 0))
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Most In-Demand Role</div>
                    <div class="metric-value-large">{most_demand['role']}</div>
                    <div class="metric-label-dark">{most_demand['total_applicants']} applicants</div>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        if employee_data and employee_data.get('employees'):
            employees = employee_data['employees']
            
            # Apply filters
            if filters:
                if filters.get('role') and filters['role'] != 'All':
                    # Use applied_role column if it exists, otherwise use role
                    if any('applied_role' in emp for emp in employees):
                        employees = [e for e in employees if e.get('applied_role') == filters['role']]
                    else:
                        employees = [e for e in employees if e.get('role') == filters['role']]
                if filters.get('department') and filters['department'] != 'All':
                    employees = [e for e in employees if e.get('Department') == filters['department']]
                if filters.get('employee_type') and filters['employee_type'] != 'All':
                    employees = [e for e in employees if e.get('Employment Type') == filters['employee_type']]
            
            if employees:
                # Average salary
                salaries = [emp['Salary'] for emp in employees if emp.get('Salary')]
                if salaries:
                    avg_salary = sum(salaries) / len(salaries)
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">Overall Average Salary</div>
                        <div class="metric-value-large">${avg_salary:,.0f}</div>
                        <div class="metric-label-dark">Across filtered employees</div>
                    </div>
                    """, unsafe_allow_html=True)

def create_headcount_by_day_graph(filters: Dict = None):
    """Create headcount by day graph showing active employees over time"""
    st.markdown('<h3 class="section-header">Headcount by Day</h3>', unsafe_allow_html=True)
    
    try:
        employee_data = fetch_api_data("master-employee-view")
        
        if not employee_data or not employee_data.get('employees'):
            st.warning("No employee data available for headcount analysis")
            return
        
        employees = employee_data['employees']
        
        # Apply filters
        if filters:
            if filters.get('role') and filters['role'] != 'All':
                employees = [e for e in employees if e.get('applied_role') == filters['role']]
            if filters.get('department') and filters['department'] != 'All':
                employees = [e for e in employees if e.get('Department') == filters['department']]
            if filters.get('employee_type') and filters['employee_type'] != 'All':
                employees = [e for e in employees if e.get('Employment Type') == filters['employee_type']]
        
        if not employees:
            st.info("No employees found with the selected filters")
            return
        
        # Create DataFrame for analysis
        df = pd.DataFrame(employees)
        
        # Convert dates and handle missing values
        df['start_date'] = pd.to_datetime(df['Start Date'], errors='coerce')
        df['end_date'] = pd.to_datetime(df['End Date'], errors='coerce')
        
        # Filter out employees with invalid start dates
        valid_employees = df.dropna(subset=['start_date'])
        
        if valid_employees.empty:
            st.warning("No employees with valid start dates found")
            return
        
        # Create date range for analysis (last 2 years to future 6 months)
        end_date = pd.Timestamp.now() + pd.DateOffset(months=6)
        start_date = pd.Timestamp.now() - pd.DateOffset(years=2)
        
        # Generate daily dates
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Calculate headcount for each day
        headcount_data = []
        
        for date in date_range:
            # Count employees active on this date
            active_employees = valid_employees[
                (valid_employees['start_date'] <= date) & 
                ((valid_employees['end_date'].isna()) | (valid_employees['end_date'] > date))
            ]
            
            headcount_data.append({
                'date': date,
                'headcount': len(active_employees)
            })
        
        headcount_df = pd.DataFrame(headcount_data)
        
        if not headcount_df.empty:
            # Create line chart
            fig = px.line(
                headcount_df,
                x='date',
                y='headcount',
                title='Headcount by Day',
                labels={'date': 'Date', 'headcount': 'Active Employees'},
                line_shape='linear'
            )
            
            # Customize the chart
            fig.update_layout(
                height=400,
                xaxis_title="Date",
                yaxis_title="Active Employees",
                hovermode='x unified'
            )
            
            # Add current headcount annotation
            current_headcount = headcount_df['headcount'].iloc[-1]
            fig.add_annotation(
                x=headcount_df['date'].iloc[-1],
                y=current_headcount,
                text=f"Current: {current_headcount}",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-40
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show summary statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                min_headcount = headcount_df['headcount'].min()
                st.metric("Lowest Headcount", f"{min_headcount}")
            
            with col2:
                max_headcount = headcount_df['headcount'].max()
                st.metric("Peak Headcount", f"{max_headcount}")
            
            with col3:
                avg_headcount = round(headcount_df['headcount'].mean(), 1)
                st.metric("Average Headcount", f"{avg_headcount}")
            
            # Show growth trend
            if len(headcount_df) > 30:  # Only show trend if we have enough data
                recent_trend = headcount_df.tail(30)
                if recent_trend['headcount'].iloc[-1] > recent_trend['headcount'].iloc[0]:
                    st.success("📈 **Growth Trend**: Headcount has been increasing recently")
                elif recent_trend['headcount'].iloc[-1] < recent_trend['headcount'].iloc[0]:
                    st.warning("📉 **Decline Trend**: Headcount has been decreasing recently")
                else:
                    st.info("➡️ **Stable Trend**: Headcount has remained relatively stable")
        
        else:
            st.warning("No headcount data available")
            
    except Exception as e:
        st.error(f"Error creating headcount graph: {str(e)}")
        st.info("Please check if the API is running and data is available")

def get_available_filters():
    """Get available filter options from API data"""
    hiring_metrics = fetch_api_data("hiring-metrics")
    employee_data = fetch_api_data("master-employee-view")
    
    filters = {
        'roles': ['All'],
        'departments': ['All'],
        'employee_types': ['All']
    }
    
    if hiring_metrics and hiring_metrics.get('metrics'):
        roles = list(set([m.get('role', '') for m in hiring_metrics['metrics'] if m.get('role')]))
        departments = list(set([m.get('department', '') for m in hiring_metrics['metrics'] if m.get('department') and m.get('department') != 'Unknown']))
        filters['roles'].extend(sorted(roles))
        # Only add departments if they're not all "Unknown"
        if departments:
            filters['departments'].extend(sorted(departments))
    
    if employee_data and employee_data.get('employees'):
        employee_types = list(set([e.get('employment_type', '') for e in employee_data['employees'] if e.get('employment_type')]))
        filters['employee_types'].extend(sorted(employee_types))
    
    return filters

def main():
    """Main dashboard function"""
    st.markdown('<h1 class="main-header">MrBeast HR Analytics</h1>', unsafe_allow_html=True)
    
    # Check API health
    if not check_api_health():
        st.error("❌ API is not available. Please ensure the API server is running.")
        return
    
    # Sidebar with logo and filters
    with st.sidebar:
        # Add MrBeast logo
        logo_base64 = get_logo_base64()
        if logo_base64:
            st.markdown(f"""
            <div class="logo-container">
                <img src="{logo_base64}" alt="MrBeast Logo">
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="logo-container">
                <h2>MrBeast HR Analytics</h2>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("## 📊 MrBeast HR Analytics")
        
        # Use Streamlit's native help tooltip with proper formatting
        st.markdown("### Core Metrics", help="""
**Core Metrics Definitions:**

📈 **Hiring Performance**
Conversion rates and time-to-hire analysis

👥 **Employment Types**
Full-time vs Contractor analysis

💰 **Salary Analysis**
By role and department

⏱️ **Tenure Analysis**
Employee retention insights

📊 **Additional Metrics**
Meaningful business insights
        """)
        
        # Filters section
        st.markdown("### 🔍 Filters")
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        
        available_filters = get_available_filters()
        
        selected_role = st.selectbox(
            "Role:",
            available_filters['roles'],
            help="Filter data by specific role"
        )
        
        selected_department = st.selectbox(
            "Department:",
            available_filters['departments'],
            help="Filter data by specific department"
        )
        
        selected_employee_type = st.selectbox(
            "Employee Type:",
            available_filters['employee_types'],
            help="Filter data by employment type"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Create filters dictionary
        filters = {
            'role': selected_role,
            'department': selected_department,
            'employee_type': selected_employee_type
        }
    
    # Fetch core data
    hiring_metrics = fetch_api_data("hiring-metrics")
    status_summary = fetch_api_data("applicants/status-summary")
    
    if not hiring_metrics:
        st.error("Unable to fetch hiring metrics data")
        return
    
    # Calculate core KPIs
    total_applicants, conversion_rate, avg_time_to_hire, in_flight_candidates, completed_applications = calculate_core_kpis(
        hiring_metrics['metrics'], status_summary, filters
    )
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Executive Overview", 
        "🎯 Hiring Analytics", 
        "👥 Employment Types", 
        "💰 Salary Analysis", 
        "⏱️ Tenure Analysis", 
        "📈 Additional Insights"
    ])
    
    # Tab 1: Executive Overview
    with tab1:
        st.markdown('<h2 class="section-header">Executive Overview</h2>', unsafe_allow_html=True)
        
        # Display core KPI cards
        create_core_kpi_cards(total_applicants, conversion_rate, avg_time_to_hire, in_flight_candidates, completed_applications)
        
        # Headcount by day graph
        create_headcount_by_day_graph(filters)
    
    # Tab 2: Hiring Analytics
    with tab2:
        st.markdown('<h2 class="section-header">Hiring Analytics</h2>', unsafe_allow_html=True)
        
        # Create hiring chart with filters
        create_hiring_metrics_chart(hiring_metrics['metrics'], filters)
        
        # Pipeline visualization
        create_pipeline_visualization(filters)
    
    # Tab 3: Employment Types
    with tab3:
        # Employment type analysis with filters
        create_employment_type_analysis(filters)
    
    # Tab 4: Salary Analysis
    with tab4:
        # Salary analysis with filters and analysis type selector
        create_salary_analysis(filters)
    
    # Tab 5: Tenure Analysis
    with tab5:
        # Tenure analysis with filters
        create_tenure_analysis(filters)
    
    # Tab 6: Additional Insights
    with tab6:
        st.markdown('<h2 class="section-header">Additional Insights</h2>', unsafe_allow_html=True)
        
        # Additional metrics with filters
        create_additional_metrics(filters)

if __name__ == "__main__":
    main() 