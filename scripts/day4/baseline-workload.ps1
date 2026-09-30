[CmdletBinding()]
param(
    [ValidateRange(60, 7200)]
    [int]$DurationSeconds = 3900,
    [ValidateRange(5, 300)]
    [int]$IntervalSeconds = 15,
    [string]$ApiBaseUrl = "http://127.0.0.1:18000",
    [Parameter(Mandatory)]
    [string]$LogPath
)

$ErrorActionPreference = "Stop"
$started = [DateTimeOffset]::Now
$deadline = $started.AddSeconds($DurationSeconds)
$attempts = 0
$successes = 0
$failures = 0

"started_at=$($started.ToString('o')) duration_seconds=$DurationSeconds interval_seconds=$IntervalSeconds" |
    Set-Content -LiteralPath $LogPath -Encoding utf8

try {
    while ([DateTimeOffset]::Now -lt $deadline) {
        $attempts++
        $at = [DateTimeOffset]::Now
        try {
            $health = Invoke-WebRequest -UseBasicParsing "$ApiBaseUrl/healthz" -TimeoutSec 5
            $payload = @{question = "Summarize the local InsightHub architecture."} | ConvertTo-Json -Compress
            $chat = Invoke-WebRequest -UseBasicParsing "$ApiBaseUrl/chat" -Method Post `
                -ContentType "application/json" -Body $payload -TimeoutSec 30
            $successes++
            "$($at.ToString('o')) health=$($health.StatusCode) chat=$($chat.StatusCode)" |
                Add-Content -LiteralPath $LogPath -Encoding utf8
        }
        catch {
            $failures++
            "$($at.ToString('o')) request=FAILED category=$($_.Exception.GetType().Name)" |
                Add-Content -LiteralPath $LogPath -Encoding utf8
        }
        Start-Sleep -Seconds $IntervalSeconds
    }
}
finally {
    $ended = [DateTimeOffset]::Now
    "ended_at=$($ended.ToString('o')) attempts=$attempts successes=$successes failures=$failures" |
        Add-Content -LiteralPath $LogPath -Encoding utf8
}
