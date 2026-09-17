$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
 python -m PyInstaller --noconfirm --clean --onefile --windowed --name DQXI-English-Translation-Builder --add-data 'release:release' --add-data 'LICENSE:.' --add-data 'licenses:licenses' --add-data 'README.md:.' tools/build_gui.py
 if ($LASTEXITCODE -ne 0) { throw 'Executable packaging failed' }
 Write-Output 'Built dist/DQXI-English-Translation-Builder.exe. Users do not need Python.'
} finally {
 Pop-Location
}
