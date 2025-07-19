# FoodLens Database Backup & Recovery System

## 📋 Overview

This directory contains automated backup and recovery scripts for the FoodLens PostgreSQL database. The system supports multiple environments (development, staging, production) and provides both manual and scheduled backup capabilities.

## 🗂️ Files

- `backup_database.ps1` - Main backup script (Windows PowerShell)
- `backup_database.sh` - Main backup script (Linux/Mac Bash)
- `restore_database.ps1` - Database restore script
- `setup_backup_schedule.ps1` - Automated backup scheduler
- `README.md` - This documentation file

## 🚀 Quick Start

### Manual Backup

```powershell
# Development environment
.\backup_database.ps1

# Production environment
.\backup_database.ps1 -Environment production

# Staging environment
.\backup_database.ps1 -Environment staging
```

### Setup Automated Backups

```powershell
# Setup daily backup at 2:00 AM (requires Administrator privileges)
.\setup_backup_schedule.ps1 -Environment production -DailyTime "02:00"

# Remove automated backup
.\setup_backup_schedule.ps1 -Environment production -Remove
```

### Restore Database

```powershell
# Restore from backup file
.\restore_database.ps1 -BackupFile "backups\foodlens_prod_20241219_020000.zip"

# Force restore to production (skips confirmation)
.\restore_database.ps1 -BackupFile "backup.zip" -Environment production -Force
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with database configurations:

```env
# Development
DEV_DB_HOST=localhost
DEV_DB_PORT=5432
DEV_DB_NAME=foodlens_dev
DEV_DB_USER=postgres
DEV_DB_PASSWORD=your_password

# Staging
STAGING_DB_HOST=staging-db.example.com
STAGING_DB_PORT=5432
STAGING_DB_NAME=foodlens_staging
STAGING_DB_USER=postgres
STAGING_DB_PASSWORD=staging_password

# Production
PROD_DB_HOST=prod-db.example.com
PROD_DB_PORT=5432
PROD_DB_NAME=foodlens_prod
PROD_DB_USER=postgres
PROD_DB_PASSWORD=production_password
```

### Script Configuration

Edit the following variables in the scripts:

- `$MaxBackups` - Number of backup files to retain (default: 30)
- `$BackupDir` - Directory to store backup files
- `$LogFile` - Location of backup log file

## 📁 Backup Format

### File Naming Convention

```
{database_name}_{environment}_{timestamp}.zip
{database_name}_{environment}_{timestamp}.meta
```

Example:
- `foodlens_prod_20241219_020000.zip` - Compressed backup file
- `foodlens_prod_20241219_020000.meta` - Backup metadata (JSON)

### Metadata Format

```json
{
    "environment": "production",
    "database": "foodlens_prod",
    "host": "prod-db.example.com",
    "port": "5432",
    "backup_time": "2024-12-19T02:00:00Z",
    "backup_file": "foodlens_prod_20241219_020000.zip",
    "original_size": "15.2 MB",
    "compressed_size": "3.8 MB",
    "backup_type": "full",
    "created_by": "SYSTEM",
    "script_version": "1.0"
}
```

## 🔒 Security Considerations

### Password Management

1. **Environment Variables**: Store passwords in `.env` file (not in version control)
2. **Windows Credential Manager**: For production, consider using Windows Credential Manager
3. **Azure Key Vault**: For cloud deployments, use Azure Key Vault or similar
4. **File Permissions**: Ensure backup files have restricted access

### Access Control

```powershell
# Set restrictive permissions on backup directory
icacls "backups" /inheritance:d
icacls "backups" /grant:r "SYSTEM:(OI)(CI)F"
icacls "backups" /grant:r "Administrators:(OI)(CI)F"
```

## 📊 Monitoring & Logging

### Log Files

- `backup.log` - Backup operation logs
- `restore.log` - Restore operation logs

### Task Scheduler Monitoring

```powershell
# Check backup task status
Get-ScheduledTask -TaskName "FoodLens-DB-Backup-*"

# View task history
Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-TaskScheduler/Operational'; ID=201} | 
Where-Object {$_.Message -like "*FoodLens*"}
```

### Log Analysis

```powershell
# View recent backup logs
Get-Content "backup.log" | Select-Object -Last 50

# Find failed backups
Select-String -Path "backup.log" -Pattern "ERROR"
```

## 🚨 Disaster Recovery

### Recovery Procedures

1. **Identify Recovery Point**: Choose appropriate backup file
2. **Verify Backup Integrity**: Check metadata and file size
3. **Create Pre-restore Backup**: Automatic safety backup
4. **Execute Restore**: Run restore script
5. **Verify Data Integrity**: Check application functionality

### Recovery Time Objectives (RTO)

- **Development**: 30 minutes
- **Staging**: 15 minutes  
- **Production**: 5 minutes

### Recovery Point Objectives (RPO)

- **Development**: 24 hours
- **Staging**: 12 hours
- **Production**: 1 hour (with additional incremental backups if needed)

## 📋 Maintenance Tasks

### Weekly Tasks

1. Verify backup completion
2. Check disk space usage
3. Test restore procedure (non-production)
4. Review backup logs for errors

### Monthly Tasks

1. Update backup retention policy
2. Test disaster recovery procedures
3. Review and update documentation
4. Audit backup security settings

### Quarterly Tasks

1. Full disaster recovery drill
2. Review and update RTO/RPO targets
3. Update backup and recovery documentation
4. Security audit of backup processes

## 🔧 Troubleshooting

### Common Issues

#### "pg_dump not found"
```powershell
# Add PostgreSQL to PATH
$env:PATH += ";C:\Program Files\PostgreSQL\15\bin"

# Or specify full path in script
$PgDumpPath = "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe"
```

#### "Permission denied" 
```powershell
# Run PowerShell as Administrator
# Check file permissions
icacls "backup_database.ps1"

# Set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### "Authentication failed"
```powershell
# Verify database credentials
psql -h localhost -U postgres -d foodlens_dev -c "SELECT 1;"

# Check .env file format (no spaces around =)
DB_PASSWORD=password_here  # Correct
DB_PASSWORD = password     # Incorrect
```

#### "Disk space full"
```powershell
# Check available space
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, FreeSpace, Size

# Clean old backups manually
Get-ChildItem "backups\*.zip" | Sort-Object LastWriteTime | Select-Object -SkipLast 10 | Remove-Item
```

### Debug Mode

Add `-Verbose` flag to scripts for detailed output:

```powershell
.\backup_database.ps1 -Environment production -Verbose
```

## 📞 Support

For backup and recovery issues:

1. Check log files first
2. Verify database connectivity
3. Confirm script permissions
4. Review environment variables
5. Contact system administrator

---

## 📝 Change Log

### Version 1.0 (2024-12-19)
- Initial backup system implementation
- PowerShell and Bash script versions
- Automated scheduling capabilities
- Metadata tracking and logging
- Security hardening features
