# ARTEX + local Qwen4B full-chain drill. Loopback only.
$ErrorActionPreference = "Continue"
$PG = "D:\refs\pg-portable\pgsql"
$AR = "D:\refs\ARTEX-release\artex-0.3.29-windows-amd64"
$OL = "D:\soft\scoop\apps\ollama\current\ollama.exe"
$LOG = "C:\Users\Administrator\Desktop\Date\log\2026-11-25-artex-fullchain"
$env:OLLAMA_MODELS = "D:\OllamaModels"
$env:OLLAMA_HOST = "0.0.0.0:11434"

function Say($m) { Write-Output ((Get-Date -Format 'HH:mm:ss') + " " + $m) }

Say "=== 1/6 Ollama ==="
Start-Process -FilePath $OL -ArgumentList "serve" -WindowStyle Hidden | Out-Null
Start-Sleep -Seconds 4
try { $t=Invoke-RestMethod "http://127.0.0.1:11434/api/tags" -TimeoutSec 5; Say ("Ollama OK models=" + $t.models.Count) } catch { Say "Ollama FAIL" }

Say "=== 2/6 PostgreSQL ==="
Start-Process -FilePath "$PG\bin\postgres.exe" -ArgumentList "-D","$PG\data" -WindowStyle Hidden | Out-Null
Start-Sleep -Seconds 12
& "$PG\bin\pg_isready.exe" -h 127.0.0.1 -p 5432 2>&1 | ForEach-Object { Say ("PG: " + $_) }

Say "=== 3/6 Set 4B profile ==="
$env:PGPASSWORD = "artex-local-drill-2026"
& "$PG\bin\psql.exe" -h 127.0.0.1 -U artex -d artex -c "UPDATE llm_profiles SET name='Local-Ollama-Qwen4B', model='qwen3.5:4b', context_window_k=8, max_tokens=1024 WHERE id=1;" 2>&1 | ForEach-Object { Say ("DB: " + $_) }
& "$PG\bin\psql.exe" -h 127.0.0.1 -U artex -d artex -c "UPDATE explorations SET status='stopped' WHERE status IN ('running','created');" 2>&1 | ForEach-Object { Say ("Cleanup: " + $_) }

Say "=== 4/6 ARTEX ==="
$env:ARTEX_CONFIG = "$AR\config.json"
Start-Process -FilePath "$AR\artex.exe" -ArgumentList "-addr","127.0.0.1:8787","-proxy","127.0.0.1:8788" -WindowStyle Hidden -WorkingDirectory $AR | Out-Null
Start-Sleep -Seconds 6
try { $h=Invoke-WebRequest "http://127.0.0.1:8787/health" -TimeoutSec 5; Say ("ARTEX health HTTP " + $h.StatusCode) } catch { Say "ARTEX FAIL" }

Say "=== 5/6 Target ==="
Start-Process -FilePath "python" -ArgumentList "$LOG\target_http.py" -WindowStyle Hidden -WorkingDirectory $LOG | Out-Null
Start-Sleep -Seconds 3
try { $h=Invoke-WebRequest "http://127.0.0.1:9099/health" -TimeoutSec 5; Say ("Target HTTP " + $h.StatusCode) } catch { Say "Target not up" }

Say "=== 6/6 Create task and observe ==="
$tok = [IO.File]::ReadAllText("$LOG\token.txt").Trim()
$hdr = @{ "Authorization" = "Bearer $tok"; "Content-Type" = "application/json" }
$body = '{"name":"4B autonomous test","description":"Local target 127.0.0.1:9099 only, loopback. Verify 4B drives ARTEX tool calls.","goal":"Check if oauth/demo redirect leaks client_secret","targets":["127.0.0.1:9099"]}'
try {
  $new = Invoke-RestMethod -Uri "http://127.0.0.1:8787/api/explorations" -Method Post -Headers $hdr -Body $body -TimeoutSec 15
  Say ("Create result: " + ($new | ConvertTo-Json -Compress -Depth 3))
} catch { Say ("Create FAIL: " + $_.Exception.Message) }

for ($i=1; $i -le 6; $i++) {
  Start-Sleep -Seconds 15
  try {
    $s = Invoke-RestMethod -Uri "http://127.0.0.1:8787/api/stats" -Headers $hdr -TimeoutSec 5
    $a = $s.active_task
    $it = 0; $ot = 0
    if ($a.tokens) { $it = $a.tokens.input_tokens; $ot = $a.tokens.output_tokens }
    Say ("Sample$i task=" + $a.id + " running=" + $a.running + " llm_in_flight=" + $a.llm_in_flight + " goals=" + $a.goals_met + "/" + $a.goals_total + " tokens=" + $it + "+" + $ot)
  } catch { Say ("Sample$i FAIL") }
}
Say "=== DONE ==="
