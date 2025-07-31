# Clear Database Tables Script
# Use this to clear all data and start fresh

param(
    [string]$DatabaseUrl = "postgresql://hr_user:hr_password@localhost:5432/mrbeast_hr"
)

Write-Host "🗑️ Clearing database tables..." -ForegroundColor Red

# SQL commands to clear tables
$clearCommands = @(
    "DELETE FROM hr_analytics.applicants;",
    "DELETE FROM hr_analytics.employees;", 
    'DELETE FROM hr_analytics."Employment type";',
    "ALTER SEQUENCE hr_analytics.applicants_id_seq RESTART WITH 1;",
    "ALTER SEQUENCE hr_analytics.employees_id_seq RESTART WITH 1;",
    'ALTER SEQUENCE hr_analytics."Employment type_id_seq" RESTART WITH 1;'
)

try {
    # Connect to database and execute clear commands
    $connectionString = $DatabaseUrl.Replace("postgresql://", "")
    $parts = $connectionString.Split("@")
    $credentials = $parts[0].Split(":")
    $hostPort = $parts[1].Split("/")
    $host = $hostPort[0].Split(":")[0]
    $port = $hostPort[0].Split(":")[1]
    $database = $hostPort[1]
    $username = $credentials[0]
    $password = $credentials[1]

    foreach ($command in $clearCommands) {
        Write-Host "Executing: $command" -ForegroundColor Gray
        & psql -h $host -p $port -U $username -d $database -c $command
    }
    
    Write-Host "✅ Database tables cleared successfully!" -ForegroundColor Green
    Write-Host "You can now run the pipeline to load fresh data." -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Error clearing database: $_" -ForegroundColor Red
    Write-Host "Make sure PostgreSQL is running and accessible." -ForegroundColor Yellow
} 