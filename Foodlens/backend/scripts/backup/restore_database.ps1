# FoodLens PostgreSQL Database Restore Script - PowerShell Version
# This script restores FoodLens database from backup files
# Usage: .\restore_database.ps1 -BackupFile "path\to\backup.zip" [-Environment "development"] [-Force]

param(
    [Parameter(Mandatory=$true)]
    [string]$BackupFile,
    [string]$Environment = "development",
    [switch]$Force
)

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogFile = Join-Path $ScriptDir "restore.log"
$TempDir = Join-Path $ScriptDir "temp"

# Logging function
function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] $Message"
    Write-Output $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

# Load environment variables from .env file
$EnvFile = Join-Path (Split-Path -Parent (Split-Path -Parent $ScriptDir)) ".env"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# Database configuration based on environment
switch ($Environment) {
    "production" {
        $DbHost = $env:PROD_DB_HOST ?? "localhost"
        $DbPort = $env:PROD_DB_PORT ?? "5432"
        $DbName = $env:PROD_DB_NAME ?? "foodlens_prod"
        $DbUser = $env:PROD_DB_USER ?? "postgres"
        $DbPassword = $env:PROD_DB_PASSWORD
    }
    "staging" {
        $DbHost = $env:STAGING_DB_HOST ?? "localhost"
        $DbPort = $env:STAGING_DB_PORT ?? "5432"
        $DbName = $env:STAGING_DB_NAME ?? "foodlens_staging"
        $DbUser = $env:STAGING_DB_USER ?? "postgres"
        $DbPassword = $env:STAGING_DB_PASSWORD
    }
    default {
        $DbHost = $env:DEV_DB_HOST ?? "localhost"
        $DbPort = $env:DEV_DB_PORT ?? "5432"
        $DbName = $env:DEV_DB_NAME ?? "foodlens_dev"
        $DbUser = $env:DEV_DB_USER ?? "postgres"
        $DbPassword = $env:DEV_DB_PASSWORD
    }
}

try {
    Write-Log "Starting restore for $Environment environment"
    Write-Log "Database: $DbName on ${DbHost}:${DbPort}"
    Write-Log "Backup file: $BackupFile"

    # Verify backup file exists
    if (!(Test-Path $BackupFile)) {
        throw "Backup file not found: $BackupFile"
    }

    # Safety check for production
    if ($Environment -eq "production" -and !$Force) {
        $Confirmation = Read-Host "WARNING: You are about to restore to PRODUCTION database. Type 'YES' to continue"
        if ($Confirmation -ne "YES") {
            Write-Log "Restore cancelled by user"
            return
        }
    }

    # Create temp directory
    if (!(Test-Path $TempDir)) {
        New-Item -ItemType Directory -Path $TempDir -Force | Out-Null
    }

    # Extract backup file
    Write-Log "Extracting backup file..."
    $ExtractPath = Join-Path $TempDir "restore_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Expand-Archive -Path $BackupFile -DestinationPath $ExtractPath

    # Find SQL file in extracted content
    $SqlFile = Get-ChildItem -Path $ExtractPath -Filter "*.sql" | Select-Object -First 1
    if (!$SqlFile) {
        throw "No SQL file found in backup archive"
    }

    Write-Log "Found SQL file: $($SqlFile.Name)"

    # Set PostgreSQL password environment variable
    $env:PGPASSWORD = $DbPassword

    # Check if psql is available
    $PsqlPath = Get-Command "psql" -ErrorAction SilentlyContinue
    if (!$PsqlPath) {
        # Try common PostgreSQL installation paths
        $CommonPaths = @(
            "${env:ProgramFiles}\PostgreSQL\*\bin\psql.exe",
            "${env:ProgramFiles(x86)}\PostgreSQL\*\bin\psql.exe"
        )
        
        foreach ($Path in $CommonPaths) {
            $Found = Get-ChildItem $Path -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($Found) {
                $PsqlPath = $Found.FullName
                break
            }
        }
    }

    if (!$PsqlPath) {
        throw "psql not found. Please ensure PostgreSQL client tools are installed and in PATH."
    }

    Write-Log "Using psql at: $($PsqlPath.Source ?? $PsqlPath)"

    # Create database backup before restore (if database exists)
    Write-Log "Creating pre-restore backup..."
    $PreRestoreBackup = Join-Path $TempDir "pre_restore_${DbName}_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
    
    $TestConnection = @(
        "--host=$DbHost",
        "--port=$DbPort",
        "--username=$DbUser",
        "--dbname=$DbName",
        "--command=SELECT 1;"
    )

    $ConnectionTest = & $PsqlPath @TestConnection 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Log "Database exists, creating pre-restore backup..."
        $BackupArgs = @(
            "--host=$DbHost",
            "--port=$DbPort",
            "--username=$DbUser",
            "--dbname=$DbName",
            "--no-password",
            "--clean",
            "--if-exists",
            "--create",
            "--format=plain",
            "--file=$PreRestoreBackup"
        )
        
        $PgDumpPath = $PsqlPath -replace "psql\.exe$", "pg_dump.exe"
        & $PgDumpPath @BackupArgs
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Pre-restore backup created: $PreRestoreBackup"
        } else {
            Write-Log "WARNING: Pre-restore backup failed, continuing with restore..."
        }
    }

    # Restore database
    Write-Log "Restoring database from: $($SqlFile.FullName)"
    $RestoreArgs = @(
        "--host=$DbHost",
        "--port=$DbPort",
        "--username=$DbUser",
        "--no-password",
        "--file=$($SqlFile.FullName)"
    )

    & $PsqlPath @RestoreArgs

    if ($LASTEXITCODE -ne 0) {
        throw "Database restore failed with exit code $LASTEXITCODE"
    }

    Write-Log "Database restore completed successfully"

    # Verify restore by checking table count
    Write-Log "Verifying restore..."
    $VerifyArgs = @(
        "--host=$DbHost",
        "--port=$DbPort",
        "--username=$DbUser",
        "--dbname=$DbName",
        "--tuples-only",
        "--command=SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
    )

    $TableCount = & $PsqlPath @VerifyArgs
    if ($LASTEXITCODE -eq 0 -and $TableCount -gt 0) {
        Write-Log "Verification successful: $($TableCount.Trim()) tables found"
    } else {
        Write-Log "WARNING: Verification failed or no tables found"
    }

    # Create restore metadata
    $MetadataFile = Join-Path $TempDir "restore_$(Get-Date -Format 'yyyyMMdd_HHmmss').meta"
    $Metadata = @{
        environment = $Environment
        database = $DbName
        host = $DbHost
        port = $DbPort
        restore_time = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        backup_file = Split-Path $BackupFile -Leaf
        restored_by = $env:USERNAME
        pre_restore_backup = if (Test-Path $PreRestoreBackup) { Split-Path $PreRestoreBackup -Leaf } else { $null }
        table_count = $TableCount.Trim()
        script_version = "1.0"
    } | ConvertTo-Json -Depth 2

    Set-Content -Path $MetadataFile -Value $Metadata
    Write-Log "Restore metadata created: $MetadataFile"

    Write-Log "Restore process completed successfully"

    # Return success
    return @{
        Success = $true
        TablesRestored = $TableCount.Trim()
        PreRestoreBackup = if (Test-Path $PreRestoreBackup) { $PreRestoreBackup } else { $null }
    }

} catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    throw
} finally {
    # Clear password from environment
    Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
    
    # Clean up temp directory (optional)
    # Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
}
