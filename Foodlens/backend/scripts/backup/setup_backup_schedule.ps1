# FoodLens Database Backup Scheduler
# This script sets up automated backup tasks using Windows Task Scheduler
# Usage: .\setup_backup_schedule.ps1 [-Environment "production"] [-DailyTime "02:00"]

param(
    [string]$Environment = "development",
    [string]$DailyTime = "02:00",
    [switch]$Remove
)

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackupScript = Join-Path $ScriptDir "backup_database.ps1"
$TaskName = "FoodLens-DB-Backup-$Environment"

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "This script requires Administrator privileges. Please run as Administrator." -ForegroundColor Red
    exit 1
}

try {
    if ($Remove) {
        # Remove existing task
        Write-Host "Removing backup task: $TaskName" -ForegroundColor Yellow
        
        $ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($ExistingTask) {
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
            Write-Host "Backup task removed successfully" -ForegroundColor Green
        } else {
            Write-Host "Task not found: $TaskName" -ForegroundColor Yellow
        }
        return
    }

    # Verify backup script exists
    if (!(Test-Path $BackupScript)) {
        throw "Backup script not found: $BackupScript"
    }

    Write-Host "Setting up automated backup for $Environment environment" -ForegroundColor Cyan
    Write-Host "Daily backup time: $DailyTime" -ForegroundColor Cyan

    # Remove existing task if it exists
    $ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($ExistingTask) {
        Write-Host "Removing existing task..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }

    # Create task action
    $Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-ExecutionPolicy Bypass -File `"$BackupScript`" -Environment $Environment"

    # Create task trigger (daily at specified time)
    $Trigger = New-ScheduledTaskTrigger -Daily -At $DailyTime

    # Create task settings
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

    # Create task principal (run as SYSTEM)
    $Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

    # Register the task
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "FoodLens Database Backup for $Environment environment"

    Write-Host "Backup task created successfully!" -ForegroundColor Green
    Write-Host "Task Name: $TaskName" -ForegroundColor Green
    Write-Host "Schedule: Daily at $DailyTime" -ForegroundColor Green
    
    # Test the task
    Write-Host "`nTesting backup task..." -ForegroundColor Cyan
    Start-ScheduledTask -TaskName $TaskName
    
    # Wait a moment and check task status
    Start-Sleep -Seconds 2
    $TaskInfo = Get-ScheduledTask -TaskName $TaskName
    $LastResult = (Get-ScheduledTaskInfo -TaskName $TaskName).LastTaskResult
    
    Write-Host "Task Status: $($TaskInfo.State)" -ForegroundColor $(if ($TaskInfo.State -eq 'Ready') { 'Green' } else { 'Yellow' })
    
    if ($LastResult -eq 0) {
        Write-Host "Test run completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Test run completed with code: $LastResult" -ForegroundColor Yellow
        Write-Host "Check the backup log file for details." -ForegroundColor Yellow
    }

    # Display next run time
    $NextRun = (Get-ScheduledTaskInfo -TaskName $TaskName).NextRunTime
    if ($NextRun) {
        Write-Host "Next scheduled run: $NextRun" -ForegroundColor Cyan
    }

    Write-Host "`nTo view task details:" -ForegroundColor Gray
    Write-Host "Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
    Write-Host "`nTo remove this task:" -ForegroundColor Gray
    Write-Host ".\setup_backup_schedule.ps1 -Environment $Environment -Remove" -ForegroundColor Gray

} catch {
    Write-Host "Error setting up backup task: $($_.Exception.Message)" -ForegroundColor Red
    throw
}
