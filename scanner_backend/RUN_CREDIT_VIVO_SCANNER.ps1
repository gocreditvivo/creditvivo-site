$ErrorActionPreference = "Stop"

$BackendDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Url = "http://127.0.0.1:8082/scanner"
$HealthUrl = "http://127.0.0.1:8082/health"
$VenvPython = Join-Path $BackendDir ".venv\Scripts\python.exe"

function Test-ScannerHealth {
    try {
        $health = Invoke-RestMethod -Uri $HealthUrl -TimeoutSec 2
        return [bool]$health.ok
    } catch {
        return $false
    }
}

Set-Location $BackendDir

if (-not (Test-ScannerHealth)) {
    if (Test-Path $VenvPython) {
        $FilePath = $VenvPython
        $Arguments = @("-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8082", "--reload")
    } else {
        $FilePath = "py"
        $Arguments = @("-3.12", "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8082", "--reload")
    }

    Start-Process -FilePath $FilePath -ArgumentList $Arguments -WorkingDirectory $BackendDir -WindowStyle Minimized

    for ($i = 0; $i -lt 40; $i++) {
        Start-Sleep -Milliseconds 500
        if (Test-ScannerHealth) { break }
    }
}

Start-Process $Url
