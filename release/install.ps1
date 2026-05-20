[CmdletBinding()]
param(
    [string]$InstallDir,
    [switch]$AllUsers
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceExe = Join-Path $scriptDir 'OctoAutoClicker.exe'

if (-not (Test-Path -LiteralPath $sourceExe)) {
    throw "OctoAutoClicker.exe was not found next to install.ps1: $sourceExe"
}

if (-not $InstallDir) {
    if ($AllUsers) {
        $InstallDir = Join-Path $env:ProgramFiles 'OctoAutoClicker'
    }
    else {
        $InstallDir = Join-Path $env:LOCALAPPDATA 'Programs\OctoAutoClicker'
    }
}

$targetExe = Join-Path $InstallDir 'OctoAutoClicker.exe'
$uninstallSource = Join-Path $scriptDir 'uninstall.ps1'
$uninstallTarget = Join-Path $InstallDir 'uninstall.ps1'

New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
Copy-Item -LiteralPath $sourceExe -Destination $targetExe -Force

if (Test-Path -LiteralPath $uninstallSource) {
    Copy-Item -LiteralPath $uninstallSource -Destination $uninstallTarget -Force
}

if ($AllUsers) {
    $programsDir = [Environment]::GetFolderPath('CommonPrograms')
}
else {
    $programsDir = [Environment]::GetFolderPath('Programs')
}

$startMenuDir = Join-Path $programsDir 'OctoAutoClicker'
$shortcutPath = Join-Path $startMenuDir 'OctoAutoClicker.lnk'

New-Item -ItemType Directory -Path $startMenuDir -Force | Out-Null

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $targetExe
$shortcut.WorkingDirectory = $InstallDir
$shortcut.IconLocation = "$targetExe,0"
$shortcut.Description = 'OctoAutoClicker'
$shortcut.Save()

Write-Host "Installed OctoAutoClicker to $InstallDir"
Write-Host "Created Start Menu shortcut: $shortcutPath"
