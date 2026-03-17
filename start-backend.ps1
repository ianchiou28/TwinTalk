$ErrorActionPreference = 'Stop'

$projectRoot = $PSScriptRoot
$backendPath = Join-Path $projectRoot 'twintalk\backend'
$venvPython = Join-Path $projectRoot '.venv\Scripts\python.exe'

if (-not (Test-Path $backendPath)) {
    throw "后端目录不存在: $backendPath"
}

Push-Location $backendPath
try {
    if (Test-Path $venvPython) {
        & $venvPython app.py
    }
    else {
        python app.py
    }
}
finally {
    Pop-Location
}