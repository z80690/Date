param(
    [string]$Dir = $PSScriptRoot
)

$expected = @(
    @{ Name = "sources/sdd-cli-0009.md"; Bytes = 4627 },
    @{ Name = "sources/sdd-bp-0011.md";  Bytes = 15820 }
)

$fail = 0
foreach ($e in $expected) {
    $p = Join-Path $Dir $e.Name
    if (Test-Path -LiteralPath $p) {
        $len = (Get-Item -LiteralPath $p).Length
        if ($len -eq $e.Bytes) {
            Write-Output ("PASS " + $e.Name + " bytes=" + $len)
        } else {
            Write-Output ("FAIL " + $e.Name + " bytes=" + $len + " expected=" + $e.Bytes)
            $fail++
        }
    } else {
        Write-Output ("FAIL " + $e.Name + " missing")
        $fail++
    }
}

if ($fail -gt 0) {
    exit 1
}
exit 0