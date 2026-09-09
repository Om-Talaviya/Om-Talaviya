param(
    [string]$Username = "Om-Talaviya",
    [string]$Name = "Om Talaviya",
    [string]$Image = "",
    [switch]$Circle
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Building GitHub Profile for $Name (@$Username)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Locate Python
$pythonCmd = $null
if (Get-Command "python" -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command "py" -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
} elseif (Test-Path "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe") {
    $pythonCmd = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
} elseif (Test-Path "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe") {
    $pythonCmd = "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
} else {
    Write-Error "Python 3.10+ is required to run the profile generators."
}

Write-Host "`n[1/4] Generating Dot-Matrix Portrait..." -ForegroundColor Yellow
if ($Image -and (Test-Path $Image)) {
    & $pythonCmd scripts/dotify.py $Image -o assets/portrait --cols 88 --equalize --detail 0.5 --accent "#38bdf8"
} else {
    & $pythonCmd scripts/dotify.py -o assets/portrait --cols 88 --equalize --detail 0.5 --accent "#38bdf8"
}

Write-Host "`n[2/4] Generating Self-Rated Skills Radar..." -ForegroundColor Yellow
& $pythonCmd scripts/radar.py --data assets/skills.json -o assets/radar --accent "#38bdf8"

Write-Host "`n[3/4] Generating Live GitHub Languages Radar..." -ForegroundColor Yellow
& $pythonCmd scripts/radar.py --github $Username -o assets/radar-langs --limit 7 --values --curve 0.4 --exclude "html,css,shell,makefile,dockerfile,batchfile" --accent "#38bdf8"

Write-Host "`n[4/4] Generating Stats and Project Cards..." -ForegroundColor Yellow
& $pythonCmd scripts/cards.py --user $Username --out assets --projects assets/projects.json --accent "#38bdf8"

Write-Host "`n Profile Assets Generated Successfully in ./assets!" -ForegroundColor Green
Write-Host " Open preview.html to view your profile in Dark and Light themes.`n" -ForegroundColor Green
