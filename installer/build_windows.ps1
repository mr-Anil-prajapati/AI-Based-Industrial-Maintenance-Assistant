$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path "$PSScriptRoot\.."
$venvPath = Join-Path $projectRoot ".venv-windows"
$modelPath = Join-Path $projectRoot "models\deepseek-r1\deepseek-r1-8b-q4.gguf"

if (!(Test-Path $modelPath)) {
    throw "Model file not found at $modelPath. Place the bundled GGUF model there before building."
}

python -m venv $venvPath
& "$venvPath\Scripts\python.exe" -m pip install --upgrade pip
& "$venvPath\Scripts\python.exe" -m pip install -r "$projectRoot\requirements.txt" -r "$projectRoot\requirements-windows.txt"
& "$venvPath\Scripts\pyinstaller.exe" --clean --noconfirm "$projectRoot\build\industrial_ai_assistant.spec"

$iscc = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
if (!(Test-Path $iscc)) {
    throw "Inno Setup 6 not found. Install it, then rerun this build script."
}

& $iscc "$projectRoot\installer\Industrial-AI-Assistant.iss"
Write-Host "Installer created at build\installer\Industrial-AI-Assistant-Setup.exe"
