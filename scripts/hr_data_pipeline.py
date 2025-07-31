#!/usr/bin/env python3
"""
Advanced HR Analytics Data Pipeline
Comprehensive data pipeline with role-department mapping and data quality analysis
"""

import os
import sys
import logging
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import json
from typing import Dict, List, Tuple, Any
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/enhanced_pipeline.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AdvancedHRDataPipeline:
    """Advanced HR data pipeline with comprehensive data model and analytics"""
    
    def __init__(self, database_url: str, excel_file: str):
        self.database_url = database_url
        self.excel_file = excel_file
        self.engine = create_engine(database_url)
        self.pipeline_results = {
            'timestamp': datetime.now().isoformat(),
            'load_summary': {},
            'enhancement_summary': {},
            'validation_summary': {},
            'errors': [],
            'warnings': []
        }
        
    def run_advanced_pipeline(self) -> Dict[str, Any]:
        """Run advanced data pipeline with schema improvements"""
        logger.info("Starting Advanced HR Analytics Data Pipeline")
        logger.info("="*60)
        
        # Step 1: Load base data
        logger.info("STEP 1: Loading base data from Excel to PostgreSQL")
        load_success = self._load_base_data()
        
        # Step 2: Apply schema improvements
        logger.info("STEP 2: Applying schema improvements")
        enhancement_success = self._apply_schema_enhancements()
        
        # Step 3: Validate advanced data
        logger.info("STEP 3: Validating advanced data")
        validation_success = self._validate_enhanced_data()
        
        # Generate final summary
        self._generate_enhanced_summary(load_success, enhancement_success, validation_success)
        
        return self.pipeline_results
    
    def _load_base_data(self) -> bool:
        """Load base data from Excel to PostgreSQL"""
        try:
            # Define table mappings (same as original)
            table_mappings = {
                'Applicants': {
                    'excel_sheet': 'Applicants',
                    'db_table': 'hr_analytics.applicants',
                    'columns': ['ID', 'Name', 'Role', 'Application Date', 'Status']
                },
                'Employees': {
                    'excel_sheet': 'Employees',
                    'db_table': 'hr_analytics.employees', 
                    'columns': ['ID', 'Name', 'Salary', 'Department', 'Start Date', 'End Date']
                },
                'Employment Type': {
                    'excel_sheet': 'Employment type ',
                    'db_table': 'hr_analytics."Employment type"',
                    'columns': ['ID', 'Employment Type']
                }
            }
            
            total_loaded = 0
            load_results = {}
            
            for table_name, mapping in table_mappings.items():
                logger.info(f"Loading {table_name} table...")
                
                try:
                    # Read Excel data
                    df = pd.read_excel(
                        self.excel_file,
                        sheet_name=mapping['excel_sheet'],
                        engine='openpyxl'
                    )
                    
                    # Clean and prepare data
                    df = self._clean_dataframe(df, table_name)
                    
                    # Load to database
                    rows_loaded = self._load_table_data(df, table_name)
                    
                    load_results[table_name] = {
                        'rows_loaded': rows_loaded,
                        'status': 'success'
                    }
                    total_loaded += rows_loaded
                    
                    logger.info(f"✅ {table_name}: {rows_loaded} rows loaded")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to load {table_name}: {e}")
                    load_results[table_name] = {
                        'rows_loaded': 0,
                        'status': 'error',
                        'error': str(e)
                    }
                    self.pipeline_results['errors'].append(f"{table_name} load error: {e}")
            
            self.pipeline_results['load_summary'] = load_results
            return all(result['status'] == 'success' for result in load_results.values())
            
        except Exception as e:
            logger.error(f"Base data loading failed: {e}")
            self.pipeline_results['errors'].append(f"Base data loading error: {e}")
            return False
    
    def _apply_schema_enhancements(self) -> bool:
        """Apply schema enhancements to address data limitations"""
        try:
            enhancement_results = {}
            
            # 1. Create role-department mapping
            logger.info("Creating role-department mapping...")
            role_dept_success = self._create_role_department_mapping()
            enhancement_results['role_department_mapping'] = {
                'status': 'success' if role_dept_success else 'error'
            }
            
            # 2. Validate master employee view
            logger.info("Validating master employee view...")
            master_view_success = self._validate_master_employee_view()
            enhancement_results['master_employee_view'] = {
                'status': 'success' if master_view_success else 'error'
            }
            
            # 3. Validate enhanced hiring metrics
            logger.info("Validating enhanced hiring metrics...")
            hiring_metrics_success = self._validate_enhanced_hiring_metrics()
            enhancement_results['enhanced_hiring_metrics'] = {
                'status': 'success' if hiring_metrics_success else 'error'
            }
            
            self.pipeline_results['enhancement_summary'] = enhancement_results
            return all(result['status'] == 'success' for result in enhancement_results.values())
            
        except Exception as e:
            logger.error(f"Schema enhancement failed: {e}")
            self.pipeline_results['errors'].append(f"Schema enhancement error: {e}")
            return False
    
    def _create_role_department_mapping(self) -> bool:
        """Create role-department mapping from hired employees with validation"""
        try:
            # SQL to populate role-department mapping with enhanced validation
            sql = """
            INSERT INTO hr_analytics.role_department_mapping ("Role", "Department", "Confidence_Score", "Mapping_Type", "Validation_Status")
            SELECT DISTINCT
                a."Role",
                e."Department",
                1.00 as confidence_score,
                'Hired_Employee' as mapping_type,
                'Validated' as validation_status
            FROM hr_analytics.applicants a
            JOIN hr_analytics.employees e ON a."Name" = e."Name" 
                AND a."Status" = 'Hired'
                AND a."Application Date" <= e."Start Date"
            ON CONFLICT ("Role") DO UPDATE SET
                "Department" = EXCLUDED."Department",
                "Updated_Date" = CURRENT_TIMESTAMP,
                "Validation_Status" = CASE 
                    WHEN hr_analytics.role_department_mapping."Department" != EXCLUDED."Department" 
                    THEN 'CONFLICT_DETECTED'
                    ELSE 'Validated'
                END
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                conn.commit()
                
            # Update applicants table with department information
            update_sql = """
            UPDATE hr_analytics.applicants 
            SET "Department" = rdm."Department"
            FROM hr_analytics.role_department_mapping rdm
            WHERE hr_analytics.applicants."Role" = rdm."Role"
                AND hr_analytics.applicants."Department" IS NULL
                AND rdm."Validation_Status" = 'Validated'
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(update_sql))
                conn.commit()
                
            # Get mapping statistics and validation results
            mapping_sql = """
            SELECT 
                COUNT(*) as total_mappings,
                COUNT(DISTINCT "Department") as departments_covered,
                COUNT(DISTINCT "Role") as roles_mapped,
                COUNT(CASE WHEN "Validation_Status" = 'Validated' THEN 1 END) as validated_mappings,
                COUNT(CASE WHEN "Validation_Status" = 'CONFLICT_DETECTED' THEN 1 END) as conflict_mappings
            FROM hr_analytics.role_department_mapping
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(mapping_sql))
                stats = result.fetchone()
                
            # Get validation details
            validation_sql = """
            SELECT 
                "Role",
                "Department", 
                "Validation_Status",
                mapping_validation,
                employee_count,
                application_count
            FROM hr_analytics.role_department_validation
            ORDER BY "Role"
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(validation_sql))
                validation_results = result.fetchall()
                
            logger.info(f"✅ Role-department mapping created:")
            logger.info(f"   - Total mappings: {stats[0]}")
            logger.info(f"   - Departments covered: {stats[1]}")
            logger.info(f"   - Roles mapped: {stats[2]}")
            logger.info(f"   - Validated mappings: {stats[3]}")
            logger.info(f"   - Conflict mappings: {stats[4]}")
            
            # Log validation results
            if validation_results:
                logger.info("📊 Role-Department Validation Results:")
                for row in validation_results:
                    status_icon = "✅" if row[3] == 'VALID' else "⚠️"
                    logger.info(f"   {status_icon} {row[0]} -> {row[1]} ({row[3]}) - {row[4]} employees, {row[5]} applications")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create role-department mapping: {e}")
            self.pipeline_results['errors'].append(f"Role-department mapping error: {e}")
            return False
    
    def _validate_master_employee_view(self) -> bool:
        """Validate master employee view"""
        try:
            sql = """
            SELECT 
                COUNT(*) as total_employees,
                COUNT(CASE WHEN "Employment Type" IS NOT NULL THEN 1 END) as with_employment_type,
                COUNT(CASE WHEN applied_role IS NOT NULL THEN 1 END) as with_application_data,
                AVG(days_to_hire) as avg_days_to_hire
            FROM hr_analytics.master_employee_view
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                stats = result.fetchone()
                
            logger.info(f"✅ Master employee view: {stats[0]} employees, {stats[1]} with employment type, {stats[2]} with application data, avg {stats[3]:.1f} days to hire")
            return True
            
        except Exception as e:
            logger.error(f"❌ Master employee view validation failed: {e}")
            return False
    
    def _validate_enhanced_hiring_metrics(self) -> bool:
        """Validate enhanced hiring metrics"""
        try:
            sql = """
            SELECT 
                COUNT(*) as total_roles,
                COUNT(CASE WHEN department != 'Unknown' THEN 1 END) as roles_with_department,
                AVG(conversion_rate) as avg_conversion_rate,
                AVG(avg_time_to_hire_days) as avg_time_to_hire,
                SUM(in_pipeline_count) as total_in_pipeline
            FROM hr_analytics.enhanced_hiring_metrics
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                stats = result.fetchone()
                
            logger.info(f"✅ Enhanced hiring metrics: {stats[0]} roles, {stats[1]} with department, {stats[2]:.1f}% avg conversion, {stats[3]:.1f} avg days to hire, {stats[4]} in pipeline")
            return True
            
        except Exception as e:
            logger.error(f"❌ Enhanced hiring metrics validation failed: {e}")
            return False
    
    def _validate_enhanced_data(self) -> bool:
        """Validate enhanced data model"""
        try:
            validation_results = {}
            
            # 1. Check role-department mapping coverage
            sql = """
            SELECT 
                COUNT(DISTINCT a."Role") as total_roles,
                COUNT(DISTINCT CASE WHEN rdm."Department" IS NOT NULL THEN a."Role" END) as mapped_roles,
                ROUND(
                    (COUNT(DISTINCT CASE WHEN rdm."Department" IS NOT NULL THEN a."Role" END) * 100.0) / 
                    COUNT(DISTINCT a."Role"), 2
                ) as mapping_coverage_percent
            FROM hr_analytics.applicants a
            LEFT JOIN hr_analytics.role_department_mapping rdm ON a."Role" = rdm."Role"
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                stats = result.fetchone()
                
            validation_results['role_department_coverage'] = {
                'total_roles': stats[0],
                'mapped_roles': stats[1],
                'coverage_percent': stats[2]
            }
            
            # 2. Check employment type utilization
            sql = """
            SELECT 
                COUNT(*) as total_employees,
                COUNT(CASE WHEN et."Employment Type" IS NOT NULL THEN 1 END) as with_employment_type,
                ROUND(
                    (COUNT(CASE WHEN et."Employment Type" IS NOT NULL THEN 1 END) * 100.0) / 
                    COUNT(*), 2
                ) as employment_type_coverage
            FROM hr_analytics.employees e
            LEFT JOIN hr_analytics."Employment type" et ON e."ID" = et."ID"
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                stats = result.fetchone()
                
            validation_results['employment_type_coverage'] = {
                'total_employees': stats[0],
                'with_employment_type': stats[1],
                'coverage_percent': stats[2]
            }
            
            # 3. Check hiring metrics accuracy
            sql = """
            SELECT 
                COUNT(*) as total_roles,
                COUNT(CASE WHEN hired_count > 0 THEN 1 END) as roles_with_hires,
                COUNT(CASE WHEN conversion_rate > 0 THEN 1 END) as roles_with_conversions,
                AVG(conversion_rate) as avg_conversion_rate
            FROM hr_analytics.enhanced_hiring_metrics
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                stats = result.fetchone()
                
            validation_results['hiring_metrics_accuracy'] = {
                'total_roles': stats[0],
                'roles_with_hires': stats[1],
                'roles_with_conversions': stats[2],
                'avg_conversion_rate': stats[3]
            }
            
            self.pipeline_results['validation_summary'] = validation_results
            
            # Log validation results
            logger.info("📊 Enhanced Data Validation Results:")
            logger.info(f"  Role-Department Coverage: {validation_results['role_department_coverage']['coverage_percent']}%")
            logger.info(f"  Employment Type Coverage: {validation_results['employment_type_coverage']['coverage_percent']}%")
            logger.info(f"  Roles with Hires: {validation_results['hiring_metrics_accuracy']['roles_with_hires']}/{validation_results['hiring_metrics_accuracy']['total_roles']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Enhanced data validation failed: {e}")
            self.pipeline_results['errors'].append(f"Enhanced data validation error: {e}")
            return False
    
    def _clean_dataframe(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Clean and prepare dataframe for database loading"""
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        if table_name == 'Applicants':
            df['Status'] = df['Status'].fillna('Pending')
        elif table_name == 'Employees':
            df['End Date'] = df['End Date'].replace('NaT', None)
        
        # Ensure proper data types
        if 'Application Date' in df.columns:
            df['Application Date'] = pd.to_datetime(df['Application Date'])
        if 'Start Date' in df.columns:
            df['Start Date'] = pd.to_datetime(df['Start Date'])
        if 'End Date' in df.columns:
            df['End Date'] = pd.to_datetime(df['End Date'], errors='coerce')
        
        return df
    
    def _load_table_data(self, df: pd.DataFrame, table_name: str) -> int:
        """Load dataframe to database table"""
        try:
            # Check if table already has data
            check_sql = f"SELECT COUNT(*) FROM {table_name}"
            with self.engine.connect() as conn:
                result = conn.execute(text(check_sql))
                existing_count = result.scalar()
                
            if existing_count > 0:
                logger.info(f"Table {table_name} already has {existing_count} rows, skipping load")
                return existing_count
            
            # Load data
            rows_loaded = len(df)
            df.to_sql(
                table_name.split('.')[-1].replace('"', ''),  # Extract table name
                self.engine,
                schema='hr_analytics',
                if_exists='append',
                index=False,
                method='multi'
            )
            
            return rows_loaded
            
        except Exception as e:
            logger.error(f"Failed to load {table_name}: {e}")
            raise
    
    def _generate_enhanced_summary(self, load_success: bool, enhancement_success: bool, validation_success: bool):
        """Generate comprehensive pipeline summary"""
        self.pipeline_results['summary'] = {
            'load_success': load_success,
            'enhancement_success': enhancement_success,
            'validation_success': validation_success,
            'overall_success': all([load_success, enhancement_success, validation_success]),
            'timestamp': datetime.now().isoformat()
        }
        
        if self.pipeline_results['summary']['overall_success']:
            logger.info("🎉 Enhanced pipeline completed successfully!")
        else:
            logger.error("❌ Enhanced pipeline completed with errors")
            
        # Save detailed report
        self.save_enhanced_report()
    
    def save_enhanced_report(self):
        """Save detailed enhanced pipeline report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"logs/enhanced_pipeline_report_{timestamp}.json"
        
        try:
            with open(report_file, 'w') as f:
                json.dump(self.pipeline_results, f, indent=2, default=str)
            logger.info(f"📄 Enhanced pipeline report saved: {report_file}")
        except Exception as e:
            logger.error(f"Failed to save enhanced report: {e}")

def main():
    """Main function for enhanced data pipeline"""
    parser = argparse.ArgumentParser(description='Enhanced HR Analytics Data Pipeline')
    parser.add_argument('--database-url', required=True, help='Database connection URL')
    parser.add_argument('--excel-file', required=True, help='Excel file path')
    parser.add_argument('--validate-only', action='store_true', help='Only validate existing data')
    
    args = parser.parse_args()
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    pipeline = AdvancedHRDataPipeline(args.database_url, args.excel_file)
    
    if args.validate_only:
        logger.info("Running validation only...")
        pipeline._validate_enhanced_data()
    else:
        logger.info("Running full enhanced pipeline...")
        results = pipeline.run_advanced_pipeline()
        
        if results['summary']['overall_success']:
            logger.info("✅ Enhanced pipeline completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Enhanced pipeline failed!")
            sys.exit(1)

if __name__ == "__main__":
    main() 