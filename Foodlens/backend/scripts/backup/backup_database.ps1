# FoodLens PostgreSQL Database Backup Script - PowerShell Version
# This script creates automated backups of the FoodLens database on Windows
# Usage: .\backup_database.ps1 [environment]

param(
    [string]$Environment = "development"
)

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackupDir = Join-Path $ScriptDir "backups"
$LogFile = Join-Path $ScriptDir "backup.log"
$MaxBackups = 30

# Create backup directory if it doesn't exist
if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

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
    Write-Log "Starting backup for $Environment environment"
    Write-Log "Database: $DbName on ${DbHost}:${DbPort}"

    # Generate backup filename with timestamp
    $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $BackupFile = Join-Path $BackupDir "${DbName}_${Environment}_${Timestamp}.sql"
    $CompressedBackup = "$BackupFile.zip"

    # Set PostgreSQL password environment variable
    $env:PGPASSWORD = $DbPassword

    # Check if pg_dump is available
    $PgDumpPath = Get-Command "pg_dump" -ErrorAction SilentlyContinue
    if (!$PgDumpPath) {
        # Try common PostgreSQL installation paths
        $CommonPaths = @(
            "${env:ProgramFiles}\PostgreSQL\*\bin\pg_dump.exe",
            "${env:ProgramFiles(x86)}\PostgreSQL\*\bin\pg_dump.exe"
        )
        
        foreach ($Path in $CommonPaths) {
            $Found = Get-ChildItem $Path -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($Found) {
                $PgDumpPath = $Found.FullName
                break
            }
        }
    }

    if (!$PgDumpPath) {
        throw "pg_dump not found. Please ensure PostgreSQL client tools are installed and in PATH."
    }

    Write-Log "Using pg_dump at: $($PgDumpPath.Source ?? $PgDumpPath)"

    # Create database backup
    Write-Log "Creating backup: $BackupFile"
    $BackupArgs = @(
        "--host=$DbHost",
        "--port=$DbPort",
        "--username=$DbUser",
        "--dbname=$DbName",
        "--no-password",
        "--verbose",
        "--clean",
        "--if-exists",
        "--create",
        "--format=plain",
        "--file=$BackupFile"
    )

    & $PgDumpPath @BackupArgs
    
    if ($LASTEXITCODE -ne 0) {
        throw "pg_dump failed with exit code $LASTEXITCODE"
    }

    # Verify backup was created
    if (!(Test-Path $BackupFile)) {
        throw "Backup file was not created"
    }

    # Get backup file size
    $BackupSize = [math]::Round((Get-Item $BackupFile).Length / 1MB, 2)
    Write-Log "Backup created successfully: ${BackupSize} MB"

    # Compress backup using built-in Windows compression
    Write-Log "Compressing backup..."
    Compress-Archive -Path $BackupFile -DestinationPath $CompressedBackup -CompressionLevel Optimal
    
    # Remove uncompressed file
    Remove-Item $BackupFile

    if (Test-Path $CompressedBackup) {
        $CompressedSize = [math]::Round((Get-Item $CompressedBackup).Length / 1MB, 2)
        Write-Log "Backup compressed successfully: ${CompressedSize} MB"
    } else {
        throw "Backup compression failed"
    }

    # Create backup metadata
    $MetadataFile = Join-Path $BackupDir "${DbName}_${Environment}_${Timestamp}.meta"
    $Metadata = @{
        environment = $Environment
        database = $DbName
        host = $DbHost
        port = $DbPort
        backup_time = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        backup_file = Split-Path $CompressedBackup -Leaf
        original_size = "${BackupSize} MB"
        compressed_size = "${CompressedSize} MB"
        backup_type = "full"
        created_by = $env:USERNAME
        script_version = "1.0"
    } | ConvertTo-Json -Depth 2

    Set-Content -Path $MetadataFile -Value $Metadata
    Write-Log "Metadata file created: $MetadataFile"

    # Clean up old backups (keep only last MAX_BACKUPS)
    Write-Log "Cleaning up old backups (keeping last $MaxBackups)..."
    $OldBackups = Get-ChildItem -Path $BackupDir -Filter "${DbName}_${Environment}_*.zip" | 
                  Sort-Object LastWriteTime -Descending | 
                  Select-Object -Skip $MaxBackups

    $OldMetadata = Get-ChildItem -Path $BackupDir -Filter "${DbName}_${Environment}_*.meta" | 
                   Sort-Object LastWriteTime -Descending | 
                   Select-Object -Skip $MaxBackups

    $OldBackups + $OldMetadata | Remove-Item -Force

    # Count remaining backups
    $BackupCount = (Get-ChildItem -Path $BackupDir -Filter "${DbName}_${Environment}_*.zip").Count
    Write-Log "Cleanup completed. $BackupCount backups remaining."

    Write-Log "Backup process completed successfully"
    Write-Log "Backup location: $CompressedBackup"

    # Return success
    return @{
        Success = $true
        BackupFile = $CompressedBackup
        Size = "${CompressedSize} MB"
    }

} catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    # You can add notification logic here (email, Slack, etc.)
    throw
} finally {
    # Clear password from environment
    Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
}
