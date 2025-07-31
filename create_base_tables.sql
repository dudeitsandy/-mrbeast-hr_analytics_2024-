-- Create base tables for HR Analytics
-- These tables are needed before running the data pipeline

-- Create applicants table
CREATE TABLE IF NOT EXISTS hr_analytics.applicants (
    "ID" SERIAL PRIMARY KEY,
    "Name" VARCHAR(255),
    "Role" VARCHAR(255),
    "Status" VARCHAR(100),
    "Application Date" DATE,
    "Department" VARCHAR(255)
);

-- Create employees table
CREATE TABLE IF NOT EXISTS hr_analytics.employees (
    "ID" SERIAL PRIMARY KEY,
    "Name" VARCHAR(255),
    "Salary" INTEGER,
    "Department" VARCHAR(255),
    "Start Date" DATE,
    "End Date" DATE
);

-- Create employment type table
CREATE TABLE IF NOT EXISTS hr_analytics."Employment type" (
    "ID" INTEGER PRIMARY KEY,
    "Employment Type" VARCHAR(100)
);

-- Grant permissions
GRANT ALL PRIVILEGES ON hr_analytics.applicants TO hr_user;
GRANT ALL PRIVILEGES ON hr_analytics.employees TO hr_user;
GRANT ALL PRIVILEGES ON hr_analytics."Employment type" TO hr_user; 