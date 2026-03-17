$ErrorActionPreference = 'Stop'

$projectRoot = $PSScriptRoot
$frontendPath = Join-Path $projectRoot 'twintalk\frontend'

if (-not (Test-Path $frontendPath)) {
    throw "前端目录不存在: $frontendPath"
}

Push-Location $frontendPath
try {
    npm install
    npx vite --host 127.0.0.1 --port 3000
}
finally {
    Pop-Location
}