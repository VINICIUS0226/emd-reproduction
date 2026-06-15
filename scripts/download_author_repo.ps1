param(
    [string]$OutDir = "external"
)

$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$target = Join-Path $OutDir "EMD"
if (Test-Path $target) {
    Write-Host "Repositorio dos autores ja existe em $target"
    exit 0
}

git clone https://github.com/tianzhaotju/EMD.git $target
Write-Host "Repositorio baixado em $target"

