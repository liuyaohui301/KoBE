param(
  [string]$Database = "battery-kg",
  [string]$DumpDir = ".\\neo4j",
  [string]$Neo4jAdmin = "neo4j-admin"
)

$ErrorActionPreference = "Stop"

Write-Host "Database: $Database"
Write-Host "DumpDir:  $DumpDir"
Write-Host "Neo4jAdmin: $Neo4jAdmin"

if (-not (Test-Path -LiteralPath $DumpDir)) {
  throw "Dump directory not found: $DumpDir"
}

Write-Host ""
Write-Host "IMPORTANT: Please STOP Neo4j before running restore." -ForegroundColor Yellow
Write-Host "This script only runs neo4j-admin database load." -ForegroundColor Yellow
Write-Host ""

$cmd = "$Neo4jAdmin database load $Database --from-path `"$DumpDir`" --overwrite-destination=true"
Write-Host "Running:"
Write-Host "  $cmd"

Invoke-Expression $cmd

Write-Host ""
Write-Host "Done. Start Neo4j again after restoring."

