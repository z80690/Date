param(
    [string]$SpecDir = ".codeartsdoer\specs\sdd_agent_refactor"
)

$expected = @(
    @{ Name = "gates\m1-learn-gate.md";    Label = "M1" },
    @{ Name = "gates\m2-exam-gate.md";     Label = "M2" },
    @{ Name = "gates\m3-agent-gate.md";    Label = "M3" },
    @{ Name = "gates\m4-e2e-gate.md";      Label = "M4" },
    @{ Name = "gates\m5-compare-gate.md";  Label = "M5" },
    @{ Name = "gates\m6-strip-gate.md";    Label = "M6" },
    @{ Name = "gates\m7-delivery-gate.md"; Label = "M7" },
    @{ Name = "gates\migration-verify.md"; Label = "MIGRATION-VERIFY" },
    @{ Name = "gates\m6-variant-scan.txt"; Label = "VARIANT-SCAN" }
)

$missing = 0
foreach ($e in $expected) {
    $p = Join-Path $SpecDir $e.Name
    if (Test-Path -LiteralPath $p) {
        Write-Output ("PASS     " + $e.Label + "  " + $e.Name)
    } else {
        Write-Output ("MISSING  " + $e.Label + "  " + $e.Name)
        $missing++
    }
}

if ($missing -gt 0) {
    Write-Output ("SUMMARY: " + $missing + " file(s) missing (expected before later gates)")
    exit 1
}
Write-Output "SUMMARY: all gate evidence files present"
exit 0