param(
    [Parameter(Mandatory = $true)]
    [string]$RemoteUrl,
    [string]$RemoteName = "origin",
    [string]$BranchName = "main"
)

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))

Push-Location $repoRoot

try {
    $hasRemote = git remote get-url $RemoteName 2>$null

    if ($LASTEXITCODE -ne 0) {
        git remote add $RemoteName $RemoteUrl
    } elseif ($hasRemote -ne $RemoteUrl) {
        git remote set-url $RemoteName $RemoteUrl
    }

    $currentBranch = git branch --show-current

    if ($currentBranch -ne $BranchName) {
        git branch -M $BranchName
    }

    git push -u $RemoteName $BranchName
}
finally {
    Pop-Location
}
