[CmdletBinding()]
param(
    [string]$InstallDir,
    [switch]$AllUsers
)

$ErrorActionPreference = 'Stop'

if (-not $InstallDir) {
    if ($AllUsers) {
        $InstallDir = Join-Path $env:ProgramFiles 'OctoAutoClicker'
    }
    else {
        $InstallDir = Join-Path $env:LOCALAPPDATA 'Programs\OctoAutoClicker'
    }
}

if ($AllUsers) {
    $programsDir = [Environment]::GetFolderPath('CommonPrograms')
}
else {
    $programsDir = [Environment]::GetFolderPath('Programs')
}

$startMenuDir = Join-Path $programsDir 'OctoAutoClicker'
$shortcutPath = Join-Path $startMenuDir 'OctoAutoClicker.lnk'

if (Test-Path -LiteralPath $shortcutPath) {
    Remove-Item -LiteralPath $shortcutPath -Force
}

if ((Test-Path -LiteralPath $startMenuDir) -and -not (Get-ChildItem -LiteralPath $startMenuDir -Force)) {
    Remove-Item -LiteralPath $startMenuDir -Force
}

$resolvedInstallDir = $null
if (Test-Path -LiteralPath $InstallDir) {
    $resolvedInstallDir = (Resolve-Path -LiteralPath $InstallDir).Path
}

if ($resolvedInstallDir -and (Split-Path -Leaf $resolvedInstallDir) -eq 'OctoAutoClicker') {
    Remove-Item -LiteralPath $resolvedInstallDir -Recurse -Force
}

Write-Host "Removed OctoAutoClicker Start Menu shortcut and install directory."
