$port = 8000
$listener = netstat -ano | Select-String ":$port.*LISTENING"
if ($listener) {
    $pid = ($listener -split '\s+')[-1]
    Write-Host "Port $port is in use by PID $pid. Stopping..." -ForegroundColor Yellow
    Stop-Process -Id $pid -Force
    Start-Sleep -Seconds 2
}

Set-Location -LiteralPath $PSScriptRoot
$env:DATABASE_URL = "sqlite:///./kirana.db"
Write-Host "Starting Vyapar Sarthi Backend on port $port..." -ForegroundColor Green
Start-Process -FilePath "uvicorn" -ArgumentList "app.main:app --reload --port $port" -NoNewWindow
Start-Sleep -Seconds 3
Write-Host "Backend started! http://localhost:$port" -ForegroundColor Green
