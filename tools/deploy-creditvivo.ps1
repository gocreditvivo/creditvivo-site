param(
  [string]$Message = "Update Credit Vivo site",
  [string]$TargetBranch = "main"
)

$ErrorActionPreference = "Stop"

$Source = "C:\CreditVivo\creditvivo_v1_clean_frontend\creditvivo_v1_clean_frontend"
$Repo = "C:\CreditVivo\_GITHUB\creditvivo-site"

function Invoke-NativeChecked {
  param(
    [string]$FilePath,
    [string[]]$Arguments,
    [string]$Description
  )

  $previousPreference = $ErrorActionPreference
  try {
    # Windows PowerShell can promote harmless native stderr warnings into
    # terminating errors. The native process exit code is authoritative.
    $ErrorActionPreference = "Continue"
    & $FilePath @Arguments
    $nativeExitCode = $LASTEXITCODE
  } finally {
    $ErrorActionPreference = $previousPreference
  }

  if ($nativeExitCode -ne 0) {
    throw "$Description failed with exit code $nativeExitCode"
  }
}

function Get-CurrentGitBranch {
  $previousPreference = $ErrorActionPreference
  try {
    $ErrorActionPreference = "Continue"
    $branch = (& git branch --show-current 2>$null).Trim()
    $nativeExitCode = $LASTEXITCODE
  } finally {
    $ErrorActionPreference = $previousPreference
  }

  if ($nativeExitCode -ne 0 -or -not $branch) {
    throw "Could not determine the current Git branch."
  }
  return $branch
}

if (!(Test-Path -LiteralPath $Source)) {
  throw "Source app folder not found: $Source"
}

if (!(Test-Path -LiteralPath (Join-Path $Repo ".git"))) {
  throw "GitHub working repo not found: $Repo"
}

Set-Location $Repo

$currentBranch = Get-CurrentGitBranch
if ($currentBranch -ne $TargetBranch) {
  throw "Refusing to deploy from branch '$currentBranch'. Expected '$TargetBranch'."
}

$preexistingChanges = git status --porcelain
if ($preexistingChanges) {
  throw "Refusing to sync over a dirty working tree. Commit, stash, or remove existing changes first."
}

Write-Host "Syncing current app into GitHub working repo without purging repository-only files..."
$robocopyArgs = @(
  $Source,
  $Repo,
  "/E",
  "/XD",
  ".git",
  ".next",
  "node_modules",
  ".vercel",
  "customer-files",
  "uploads",
  "credit-reports",
  "ids",
  "_backup_before_creditvivo_full_mvp",
  "src",
  "/XF",
  ".env",
  "*.local",
  "*.pem",
  "*.key",
  "*.pfx",
  "*.pdf",
  "*.xlsx",
  "*.xls",
  "*.csv",
  "*.zip"
)

& robocopy @robocopyArgs
if ($LASTEXITCODE -gt 7) {
  throw "Robocopy failed with exit code $LASTEXITCODE"
}

Write-Host "Installing approved dependencies..."
Invoke-NativeChecked -FilePath "npm.cmd" -Arguments @("ci") -Description "npm ci"

Write-Host "Building production app..."
Invoke-NativeChecked -FilePath "npm.cmd" -Arguments @("run", "build") -Description "npm run build"

$changes = git status --porcelain
if (-not $changes) {
  Write-Host "Build passed. No changes to commit."
  exit 0
}

Write-Host "Committing verified changes..."
Invoke-NativeChecked -FilePath "git.exe" -Arguments @("add", "-A") -Description "git add"
Invoke-NativeChecked -FilePath "git.exe" -Arguments @("commit", "-m", $Message) -Description "git commit"

Write-Host "Pushing verified changes to GitHub $TargetBranch..."
Invoke-NativeChecked -FilePath "git.exe" -Arguments @("push", "origin", "HEAD:$TargetBranch") -Description "git push"

Write-Host "Done. Verify https://www.creditvivo.com after Vercel finishes."

