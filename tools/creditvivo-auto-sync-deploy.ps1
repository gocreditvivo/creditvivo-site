
param(
  [string]$CommitMessage = "",
  [switch]$ForceBuild,
  [string]$TargetBranch = "main"
)

$ErrorActionPreference = "Stop"

$Official = "C:\CreditVivo\_OFFICIAL"
$SourceApp = "C:\CreditVivo\creditvivo_v1_clean_frontend\creditvivo_v1_clean_frontend"
$GitRepo = "C:\CreditVivo\_GITHUB\creditvivo-site"
$StagingDrive = "C:\CreditVivo\_GOOGLE_DRIVE_LOCAL_STAGING\CreditVivo"
$LogDir = Join-Path $Official "11_Automation\logs"
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$LogFile = Join-Path $LogDir "creditvivo-auto-sync-deploy-$Stamp.log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Step {
  param([string]$Message)
  $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
  Write-Host $line
  Add-Content -LiteralPath $LogFile -Value $line
}

function Invoke-RobocopySafe {
  param(
    [string]$From,
    [string]$To,
    [string[]]$ExcludeDirs = @(),
    [string[]]$ExcludeFiles = @(),
    [bool]$Mirror = $true
  )

  New-Item -ItemType Directory -Force -Path $To | Out-Null
  $copyMode = if ($Mirror) { "/MIR" } else { "/E" }
  $args = @($From, $To, $copyMode)
  if ($ExcludeDirs.Count -gt 0) { $args += "/XD"; $args += $ExcludeDirs }
  if ($ExcludeFiles.Count -gt 0) { $args += "/XF"; $args += $ExcludeFiles }

  Write-Step "Robocopy: $From -> $To"
  & robocopy @args | Add-Content -LiteralPath $LogFile
  if ($LASTEXITCODE -gt 7) {
    throw "Robocopy failed with exit code $LASTEXITCODE"
  }
}

function Invoke-NativeLogged {
  param(
    [string]$FilePath,
    [string[]]$Arguments,
    [string]$Description
  )

  $previousPreference = $ErrorActionPreference
  try {
    # Windows PowerShell can promote native stderr warnings into terminating
    # ErrorRecord objects when ErrorActionPreference is Stop. Capture all
    # output, then make the native exit code the only success/failure signal.
    $ErrorActionPreference = "Continue"
    & $FilePath @Arguments 2>&1 |
      ForEach-Object { Add-Content -LiteralPath $LogFile -Value ([string]$_) }
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

function Get-GoogleDriveCreditVivoPath {
  $candidates = @(
    "G:\My Drive\CreditVivo",
    "H:\My Drive\CreditVivo",
    "I:\My Drive\CreditVivo",
    "G:\Shared drives\CreditVivo",
    "H:\Shared drives\CreditVivo",
    "C:\Users\miste\Google Drive\My Drive\CreditVivo",
    "C:\Users\miste\My Drive\CreditVivo"
  )

  foreach ($path in $candidates) {
    if (Test-Path -LiteralPath (Split-Path $path -Parent)) {
      New-Item -ItemType Directory -Force -Path $path | Out-Null
      return $path
    }
  }

  New-Item -ItemType Directory -Force -Path $StagingDrive | Out-Null
  return $StagingDrive
}

function Sync-SafeDocsToDrive {
  $drivePath = Get-GoogleDriveCreditVivoPath
  Write-Step "Safe docs target: $drivePath"

  $excludeDirs = @(".git", ".next", ".vercel", "node_modules", "logs", "remote_repo_inspect", "10_Customer_Data_SECURE_DO_NOT_SYNC", "90_Archive_Old_Versions", "customer-files", "uploads", "credit-reports", "ids")
  $excludeFiles = @(".env", "*.pem", "*.key", "*.pfx", "*.pdf", "*.xlsx", "*.xls", "*.csv", "*.zip")

  $map = @(
    @{ Source = "."; Destination = "Official Docs" },
    @{ Source = "01_Website_App"; Destination = "Business Docs\Website App" },
    @{ Source = "02_Customer_Portal"; Destination = "Business Docs\Customer Portal" },
    @{ Source = "03_Scanner_Engine"; Destination = "Business Docs\Scanner Engine" },
    @{ Source = "04_Compliance_Legal"; Destination = "Compliance Legal" },
    @{ Source = "05_Launch_Operations"; Destination = "Launch Operations" },
    @{ Source = "06_Marketing_Sales"; Destination = "Marketing Sales" },
    @{ Source = "07_Brand_Assets"; Destination = "Brand Assets" },
    @{ Source = "08_Social_Studio"; Destination = "Business Docs\Social Studio" },
    @{ Source = "09_Vendors_APIs"; Destination = "Vendor Research" }
  )

  foreach ($item in $map) {
    $from = Join-Path $Official $item.Source
    $to = Join-Path $drivePath $item.Destination
    if (Test-Path -LiteralPath $from) {
      Invoke-RobocopySafe -From $from -To $to -ExcludeDirs $excludeDirs -ExcludeFiles $excludeFiles
    }
  }

  if (Test-Path -LiteralPath $GitRepo) {
    Invoke-RobocopySafe -From $GitRepo -To (Join-Path $drivePath "Code\creditvivo-site") -ExcludeDirs $excludeDirs -ExcludeFiles $excludeFiles
  }
}

function Sync-AppToGitRepo {
  if (!(Test-Path -LiteralPath $SourceApp)) {
    throw "Source app missing: $SourceApp"
  }
  if (!(Test-Path -LiteralPath (Join-Path $GitRepo ".git"))) {
    throw "GitHub repo missing: $GitRepo"
  }

  $excludeDirs = @(".git", ".next", "node_modules", ".vercel", "customer-files", "uploads", "credit-reports", "ids", "_backup_before_creditvivo_full_mvp", "src")
  $excludeFiles = @(".env", "*.local", "*.pem", "*.key", "*.pfx", "*.pdf", "*.xlsx", "*.xls", "*.csv", "*.zip")
  # The application source is not allowed to purge repository-only files such
  # as handoff notes, CI configuration, or routes maintained in Git.
  Invoke-RobocopySafe -From $SourceApp -To $GitRepo -ExcludeDirs $excludeDirs -ExcludeFiles $excludeFiles -Mirror $false
}

try {
  Write-Step "Credit Vivo automation started."

  Sync-SafeDocsToDrive

  Set-Location $GitRepo
  $currentBranch = Get-CurrentGitBranch
  if ($currentBranch -ne $TargetBranch) {
    throw "Refusing to deploy from branch '$currentBranch'. Expected '$TargetBranch'."
  }

  $preexistingChanges = git status --porcelain
  if ($preexistingChanges) {
    throw "Refusing to sync over a dirty working tree. Commit, stash, or remove existing changes first."
  }

  Sync-AppToGitRepo
  $changes = git status --porcelain

  if (-not $changes -and -not $ForceBuild) {
    Write-Step "No GitHub app changes found. Skipping build, commit, push."
    Write-Step "Credit Vivo automation complete."
    exit 0
  }

  Write-Step "Changes detected or build forced. Installing dependencies."
  Invoke-NativeLogged -FilePath "npm.cmd" -Arguments @("ci") -Description "npm ci"

  Write-Step "Running production build."
  Invoke-NativeLogged -FilePath "npm.cmd" -Arguments @("run", "build") -Description "npm run build"

  $changesAfterBuild = git status --porcelain
  if (-not $changesAfterBuild) {
    Write-Step "Build passed, but no commit changes remain."
    Write-Step "Credit Vivo automation complete."
    exit 0
  }

  if (-not $CommitMessage) {
    $CommitMessage = "Automated Credit Vivo update $Stamp"
  }

  Write-Step "Committing changes: $CommitMessage"
  Invoke-NativeLogged -FilePath "git.exe" -Arguments @("add", "-A") -Description "git add"
  Invoke-NativeLogged -FilePath "git.exe" -Arguments @("commit", "-m", $CommitMessage) -Description "git commit"

  Write-Step "Pushing to GitHub $TargetBranch. Vercel should auto-deploy."
  Invoke-NativeLogged -FilePath "git.exe" -Arguments @("push", "origin", "HEAD:$TargetBranch") -Description "git push"

  Sync-SafeDocsToDrive

  Write-Step "Credit Vivo automation complete."
} catch {
  Write-Step "FAILED: $($_.Exception.Message)"
  exit 1
}

