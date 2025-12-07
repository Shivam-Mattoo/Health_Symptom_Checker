# MongoDB Connection Fix Script for Windows
# Run this in PowerShell as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MongoDB Connection Fix for Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "Step 1: Adding MongoDB Firewall Rule..." -ForegroundColor Yellow
try {
    netsh advfirewall firewall add rule name="MongoDB Out" dir=out action=allow protocol=TCP remoteport=27017
    netsh advfirewall firewall add rule name="MongoDB In" dir=in action=allow protocol=TCP localport=27017
    Write-Host "[OK] Firewall rules added" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Firewall rule may already exist" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 2: Resetting Winsock Catalog..." -ForegroundColor Yellow
netsh winsock reset
Write-Host "[OK] Winsock reset complete" -ForegroundColor Green

Write-Host ""
Write-Host "Step 3: Resetting TCP/IP Stack..." -ForegroundColor Yellow
netsh int ip reset
Write-Host "[OK] TCP/IP reset complete" -ForegroundColor Green

Write-Host ""
Write-Host "Step 4: Flushing DNS Cache..." -ForegroundColor Yellow
ipconfig /flushdns
Write-Host "[OK] DNS cache flushed" -ForegroundColor Green

Write-Host ""
Write-Host "Step 5: Testing MongoDB Connectivity..." -ForegroundColor Yellow
try {
    $result = Test-NetConnection -ComputerName "healthsymptomchecker.d5oeexp.mongodb.net" -Port 27017 -WarningAction SilentlyContinue
    if ($result.TcpTestSucceeded) {
        Write-Host "[OK] MongoDB port 27017 is accessible" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] Cannot reach MongoDB on port 27017" -ForegroundColor Yellow
        Write-Host "This might be a firewall or network issue" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[WARNING] Could not test connection (this is OK)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Fix Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: You must restart your computer now!" -ForegroundColor Yellow
Write-Host ""
Write-Host "After restart, test the connection by running:" -ForegroundColor Cyan
Write-Host "  python test_mongodb.py" -ForegroundColor White
Write-Host ""

$restart = Read-Host "Do you want to restart now? (y/n)"
if ($restart -eq "y" -or $restart -eq "Y") {
    Write-Host "Restarting computer in 10 seconds..." -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to cancel" -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    Restart-Computer -Force
} else {
    Write-Host "Please restart manually before using the application." -ForegroundColor Yellow
}
