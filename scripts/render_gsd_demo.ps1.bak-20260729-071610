# Render GSD food-duo demo short via ittybitty API (Jellyfin/Plex or Pexels stock).
# Requires: backend on :11054, LLM + stock configured in Settings.
#
# Usage:
#   .\scripts\render_gsd_demo.ps1
#   .\scripts\render_gsd_demo.ps1 -BaseUrl http://127.0.0.1:11054 -LlmProvider deepseek

param(
    [string]$BaseUrl = "http://127.0.0.1:11054",
    [string]$LlmProvider = "deepseek"
)

$body = @{
    topic = "Two German Shepherd dogs taste-test the same treats — one loves everything (Yummy), one is picky (Whazzat). Funny pet food review short."
    aspect = "9:16"
    paragraph_count = 4
    clip_duration = 5
    llm_provider = $LlmProvider
    structure = "trope:pet-food-duo-review"
    style_notes = "On-screen text: Yummy, Whazzat?, 10/10, Bleh. Fast cuts ~1.5s. Search terms: german shepherd dog eating treat."
} | ConvertTo-Json

Write-Host "POST $BaseUrl/api/v1/generate"
$response = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/v1/generate" -ContentType "application/json" -Body $body
Write-Host "Job queued: $($response.job_id) status=$($response.status)"
Write-Host "Track at $BaseUrl (Jobs) or poll GET $BaseUrl/api/v1/jobs/$($response.job_id)"
