-- Enhanced HR Analytics Schema
-- Addresses data model limitations and improves analytical capabilities

-- =============================================================================
-- ENHANCED ROLE-DEPARTMENT REFERENCE TABLE
-- =============================================================================
-- Purpose: Maps roles to departments based on hired employees with validation
-- Solves: Applications lack department information issue
-- Enhancement: Validates one-to-one role-to-department mapping

CREATE TABLE hr_analytics.role_department_mapping (
    "Role" VARCHAR(255) PRIMARY KEY,
    "Department" VARCHAR(255) NOT NULL,
    "Confidence_Score" DECIMAL(3,2) DEFAULT 1.00, -- How confident we are in this mapping
    "Mapping_Type" VARCHAR(50) DEFAULT 'Hired_Employee', -- Source of mapping
    "Validation_Status" VARCHAR(50) DEFAULT 'Validated', -- Whether mapping is validated
    "Created_Date" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "Updated_Date" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for performance
CREATE INDEX idx_role_department_role ON hr_analytics.role_department_mapping ("Role");
CREATE INDEX idx_role_department_dept ON hr_analytics.role_department_mapping ("Department");

-- =============================================================================
-- ENHANCED APPLICANTS TABLE WITH DEPARTMENT
-- =============================================================================
-- Purpose: Add department column to applicants table for better analytics
-- Solves: Department information missing from applications

-- First, add department column to existing applicants table
ALTER TABLE hr_analytics.applicants ADD COLUMN IF NOT EXISTS "Department" VARCHAR(255);

-- Create index for department lookups
CREATE INDEX IF NOT EXISTS idx_applicants_department ON hr_analytics.applicants ("Department");

-- =============================================================================
-- ROLE-DEPARTMENT VALIDATION VIEW
-- =============================================================================
-- Purpose: Validate one-to-one role-to-department mapping
-- Solves: Ensures data quality for department inference

CREATE VIEW hr_analytics.role_department_validation AS
SELECT 
    rdm."Role",
    rdm."Department",
    rdm."Confidence_Score",
    rdm."Mapping_Type",
    rdm."Validation_Status",
    -- Check for conflicts (same role mapped to different departments)
    CASE 
        WHEN COUNT(*) OVER (PARTITION BY rdm."Role") > 1 THEN 'CONFLICT'
        WHEN COUNT(*) OVER (PARTITION BY rdm."Department") > 1 THEN 'MULTIPLE_ROLES'
        ELSE 'VALID'
    END as mapping_validation,
    -- Count of employees with this role
    COUNT(e."ID") as employee_count,
    -- Count of applications with this role
    COUNT(a."ID") as application_count
FROM hr_analytics.role_department_mapping rdm
LEFT JOIN hr_analytics.employees e ON e."Department" = rdm."Department"
LEFT JOIN hr_analytics.applicants a ON a."Role" = rdm."Role"
GROUP BY rdm."Role", rdm."Department", rdm."Confidence_Score", rdm."Mapping_Type", rdm."Validation_Status";

-- =============================================================================
-- MASTER EMPLOYEE VIEW
-- =============================================================================
-- Purpose: Combines employee data with application info and employment type
-- Solves: Employment type table underutilization and provides comprehensive employee view

CREATE VIEW hr_analytics.master_employee_view AS
SELECT 
    e."ID",
    e."Name",
    e."Salary",
    e."Department",
    e."Start Date",
    e."End Date",
    et."Employment Type",
    a."Role" as applied_role,
    a."Application Date",
    a."Status" as application_status,
    CASE 
        WHEN e."End Date" IS NULL THEN 'Current'
        ELSE 'Former'
    END as employment_status,
    CASE 
        WHEN e."Start Date" IS NOT NULL AND a."Application Date" IS NOT NULL THEN 
            EXTRACT(DAYS FROM (e."Start Date" - a."Application Date"))
        ELSE NULL 
    END as days_to_hire
FROM hr_analytics.employees e
LEFT JOIN hr_analytics."Employment type" et ON e."ID" = et."ID"
LEFT JOIN hr_analytics.applicants a ON e."Name" = a."Name" 
    AND a."Status" = 'Hired' 
    AND a."Application Date" <= e."Start Date";

-- =============================================================================
-- ENHANCED HIRING METRICS VIEW
-- =============================================================================
-- Purpose: Provides accurate hiring metrics that handle data limitations
-- Solves: Roles by department showing all applicants without hires issue

CREATE VIEW hr_analytics.enhanced_hiring_metrics AS
SELECT 
    a."Role",
    COALESCE(a."Department", rdm."Department", 'Unknown') as department,
    COUNT(a."ID") as total_applicants,
    COUNT(CASE WHEN a."Status" = 'Hired' THEN 1 END) as hired_count,
    COUNT(CASE WHEN a."Status" = 'Rejected' THEN 1 END) as rejected_count,
    COUNT(CASE WHEN a."Status" = 'Interviewing' THEN 1 END) as interviewing_count,
    COUNT(CASE WHEN a."Status" = 'Offer Extended' THEN 1 END) as offer_extended_count,
    COUNT(CASE WHEN a."Status" = 'Withdrawn' THEN 1 END) as withdrawn_count,
    COUNT(CASE WHEN a."Status" = 'Pending' THEN 1 END) as pending_count,
    COUNT(CASE WHEN a."Status" = 'Phone Screen' THEN 1 END) as phone_screen_count,
    CASE 
        WHEN COUNT(CASE WHEN a."Status" IN ('Hired', 'Rejected') THEN 1 END) > 0 THEN
            ROUND(
                (COUNT(CASE WHEN a."Status" = 'Hired' THEN 1 END) * 100.0) / 
                COUNT(CASE WHEN a."Status" IN ('Hired', 'Rejected') THEN 1 END), 
                2
            )
        ELSE 0 
    END as conversion_rate,
    AVG(CASE 
        WHEN a."Status" = 'Hired' AND e."Start Date" IS NOT NULL THEN 
            EXTRACT(DAYS FROM (e."Start Date" - a."Application Date"))
        ELSE NULL 
    END) as avg_time_to_hire_days,
    COUNT(CASE WHEN a."Status" NOT IN ('Hired', 'Rejected', 'Withdrawn') THEN 1 END) as in_pipeline_count
FROM hr_analytics.applicants a
LEFT JOIN hr_analytics.role_department_mapping rdm ON a."Role" = rdm."Role"
LEFT JOIN hr_analytics.employees e ON a."Name" = e."Name" 
    AND a."Status" = 'Hired'
    AND a."Application Date" <= e."Start Date"
GROUP BY a."Role", COALESCE(a."Department", rdm."Department", 'Unknown');

-- =============================================================================
-- DEPARTMENT ANALYTICS VIEW (ENHANCED)
-- =============================================================================
-- Purpose: Comprehensive department-level analytics
-- Includes: Hiring metrics, employee metrics, cost analysis

CREATE VIEW hr_analytics.department_analytics_enhanced AS
SELECT 
    d.department,
    d.total_employees,
    d.current_employees,
    d.former_employees,
    d.avg_salary,
    d.total_salary_cost,
    h.total_applications,
    h.hired_count,
    h.conversion_rate,
    h.avg_time_to_hire_days,
    h.in_pipeline_count,
    ROUND(
        CASE 
            WHEN h.total_applications > 0 THEN 
                (h.hired_count * 100.0) / h.total_applications 
            ELSE 0 
        END, 2
    ) as overall_hire_rate,
    ROUND(
        CASE 
            WHEN d.current_employees > 0 THEN 
                (h.in_pipeline_count * 100.0) / d.current_employees 
            ELSE 0 
        END, 2
    ) as pipeline_to_headcount_ratio
FROM (
    -- Employee metrics by department
    SELECT 
        "Department" as department,
        COUNT(*) as total_employees,
        COUNT(CASE WHEN "End Date" IS NULL THEN 1 END) as current_employees,
        COUNT(CASE WHEN "End Date" IS NOT NULL THEN 1 END) as former_employees,
        AVG("Salary") as avg_salary,
        SUM("Salary") as total_salary_cost
    FROM hr_analytics.employees
    GROUP BY "Department"
) d
LEFT JOIN (
    -- Hiring metrics by department
    SELECT 
        COALESCE(a."Department", rdm."Department", 'Unknown') as department,
        COUNT(a."ID") as total_applications,
        COUNT(CASE WHEN a."Status" = 'Hired' THEN 1 END) as hired_count,
        AVG(CASE 
            WHEN a."Status" = 'Hired' AND e."Start Date" IS NOT NULL THEN 
                EXTRACT(DAYS FROM (e."Start Date" - a."Application Date"))
            ELSE NULL 
        END) as avg_time_to_hire_days,
        COUNT(CASE WHEN a."Status" NOT IN ('Hired', 'Rejected', 'Withdrawn') THEN 1 END) as in_pipeline_count,
        CASE 
            WHEN COUNT(CASE WHEN a."Status" IN ('Hired', 'Rejected') THEN 1 END) > 0 THEN
                ROUND(
                    (COUNT(CASE WHEN a."Status" = 'Hired' THEN 1 END) * 100.0) / 
                    COUNT(CASE WHEN a."Status" IN ('Hired', 'Rejected') THEN 1 END), 
                    2
                )
            ELSE 0 
        END as conversion_rate
    FROM hr_analytics.applicants a
    LEFT JOIN hr_analytics.role_department_mapping rdm ON a."Role" = rdm."Role"
    LEFT JOIN hr_analytics.employees e ON a."Name" = e."Name" 
        AND a."Status" = 'Hired'
        AND a."Application Date" <= e."Start Date"
    GROUP BY COALESCE(a."Department", rdm."Department", 'Unknown')
) h ON d.department = h.department;

-- =============================================================================
-- ENHANCED DATA POPULATION SCRIPTS
-- =============================================================================

-- Populate role-department mapping from hired employees with validation
-- Note: This only maps roles for employees who came through the application process
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
    END;

-- Update applicants table with department information from role mapping
-- This will populate department for applicants where we have a validated role mapping
UPDATE hr_analytics.applicants 
SET "Department" = rdm."Department"
FROM hr_analytics.role_department_mapping rdm
WHERE hr_analytics.applicants."Role" = rdm."Role"
    AND hr_analytics.applicants."Department" IS NULL
    AND rdm."Validation_Status" = 'Validated';

-- =============================================================================
-- DATA QUALITY ANALYSIS VIEWS
-- =============================================================================
-- Purpose: Analyze data quality and coverage between applicants and employees
-- Solves: Understanding the realistic HR data scenario

CREATE VIEW hr_analytics.data_quality_analysis AS
SELECT 
    'Applicants' as data_source,
    COUNT(*) as total_records,
    COUNT(CASE WHEN "Status" = 'Hired' THEN 1 END) as hired_count,
    COUNT(CASE WHEN "Status" != 'Hired' THEN 1 END) as non_hired_count,
    COUNT(CASE WHEN "Department" IS NOT NULL THEN 1 END) as with_department,
    COUNT(CASE WHEN "Department" IS NULL THEN 1 END) as without_department
FROM hr_analytics.applicants
UNION ALL
SELECT 
    'Employees' as data_source,
    COUNT(*) as total_records,
    COUNT(CASE WHEN "End Date" IS NULL THEN 1 END) as current_employees,
    COUNT(CASE WHEN "End Date" IS NOT NULL THEN 1 END) as former_employees,
    COUNT(*) as with_department, -- All employees have department
    0 as without_department
FROM hr_analytics.employees;

-- Cross-reference view to show hiring success
CREATE VIEW hr_analytics.hiring_success_analysis AS
SELECT 
    a."Status" as application_status,
    COUNT(a."ID") as applicant_count,
    COUNT(e."ID") as employee_matches,
    ROUND(
        (COUNT(e."ID") * 100.0) / COUNT(a."ID"), 
        2
    ) as conversion_to_employee_rate
FROM hr_analytics.applicants a
LEFT JOIN hr_analytics.employees e ON a."Name" = e."Name"
GROUP BY a."Status"
ORDER BY applicant_count DESC;

-- Employee source analysis
CREATE VIEW hr_analytics.employee_source_analysis AS
SELECT 
    CASE 
        WHEN a."ID" IS NOT NULL THEN 'From_Application_Process'
        ELSE 'Direct_Hire_Or_Transfer'
    END as employee_source,
    COUNT(e."ID") as employee_count,
    ROUND(
        (COUNT(e."ID") * 100.0) / (SELECT COUNT(*) FROM hr_analytics.employees), 
        2
    ) as percentage_of_total_employees
FROM hr_analytics.employees e
LEFT JOIN hr_analytics.applicants a ON e."Name" = a."Name" AND a."Status" = 'Hired'
GROUP BY CASE 
    WHEN a."ID" IS NOT NULL THEN 'From_Application_Process'
    ELSE 'Direct_Hire_Or_Transfer'
END;

-- =============================================================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================================================

COMMENT ON TABLE hr_analytics.role_department_mapping IS 'Enhanced role-department mapping with validation - solves department inference issue';
COMMENT ON COLUMN hr_analytics.role_department_mapping."Role" IS 'Job role/title';
COMMENT ON COLUMN hr_analytics.role_department_mapping."Department" IS 'Inferred department based on hired employees';
COMMENT ON COLUMN hr_analytics.role_department_mapping."Confidence_Score" IS 'Confidence in the role-department mapping (1.00 = high confidence)';
COMMENT ON COLUMN hr_analytics.role_department_mapping."Mapping_Type" IS 'Source of the mapping (Hired_Employee, etc.)';
COMMENT ON COLUMN hr_analytics.role_department_mapping."Validation_Status" IS 'Validation status of the mapping';

COMMENT ON VIEW hr_analytics.role_department_validation IS 'Validates one-to-one role-to-department mapping and identifies conflicts';
COMMENT ON VIEW hr_analytics.master_employee_view IS 'Comprehensive employee view combining employment data, application history, and employment type';
COMMENT ON VIEW hr_analytics.enhanced_hiring_metrics IS 'Improved hiring metrics that handle data limitations and provide accurate conversion rates';
COMMENT ON VIEW hr_analytics.department_analytics_enhanced IS 'Comprehensive department analytics including hiring metrics, employee metrics, and cost analysis';

-- =============================================================================
-- GRANT PERMISSIONS
-- =============================================================================
GRANT SELECT ON hr_analytics.role_department_mapping TO analytics_user;
GRANT SELECT ON hr_analytics.role_department_validation TO analytics_user;
GRANT SELECT ON hr_analytics.master_employee_view TO analytics_user;
GRANT SELECT ON hr_analytics.enhanced_hiring_metrics TO analytics_user;
GRANT SELECT ON hr_analytics.department_analytics_enhanced TO analytics_user; 