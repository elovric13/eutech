$LogFile = "C:\Logs\ps_script.log"
$Date = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$ProcessExport = "C:\Logs\processes_$Date.csv"
$BackupSource = "C:\Users"
$BackupDest = "C:\Backup"
$BackupFile = "$BackupDest\backup_$Date.zip"

function Write-Log {
    param ([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd_HH:mm:ss"
    $entry = "[$timestamp] $Message"
    Write-Host $entry
    Add-Content -Path $LogFile -Value $entry
    }

Write-Log "Script started"

# Export processes to .csv

Write-Log "Starting process export"

Get-Process | Select-Object Name, Id, CPU, WorkingSet | Export-Csv -Path $ProcessExport -NoTypeInformation

Write-Log "Process list exported to: $ProcessExport"
Write-Log "Process export finished."

# Folder backup

Write-Log "Starting backup"

if (-not (Test-Path $BackupDest)) {
    New-Item -ItemType Directory -Path $BackupDest | Out-Null
}

try {
    Compress-Archive -Path $BackupSource -DestinationPath $BackupFile -Force
    Write-Log "Backup created successfully: $BackupFile"
} catch {
    Write-Log "ERROR: Backup failed - $_"
}

Write-Log "Backup finished"

# CPU usage alert

$CpuThreshold = 80

Write-Log "Checking CPU usage"

$CpuLoad = (Get-CimInstance -ClassName Win32_Processor |
    Measure-Object -Property LoadPercentage -Average).Average

Write-Log "Current CPU usage: $CpuLoad%"

if ($CpuLoad -gt $CpuThreshold) {
    $AlertMessage = "ALERT: CPU usage is at $CpuLoad%, which exceeds the threshold of $CpuThreshold%."
    Write-Log $AlertMessage
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show($AlertMessage, "CPU Alert", "OK", "Warning")
} else {
    Write-Log "CPU usage is within normal range."
}

Write-Log "Script completed"