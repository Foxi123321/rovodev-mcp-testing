# Simple async image analysis with llava
param(
    [Parameter(Mandatory=$true)]
    [string]$ImagePath,
    
    [string]$Prompt = "Describe this image in detail",
    
    [string]$OutputFile = ""
)

$jobId = [guid]::NewGuid().ToString().Substring(0,8)

if ($OutputFile -eq "") {
    $OutputFile = "C:\Users\ggfuc\.rovodev\mcp_testing_server\screenshots\analysis_$jobId.txt"
}

Write-Host "🔥 Starting analysis with job ID: $jobId" -ForegroundColor Cyan
Write-Host "📁 Output file: $OutputFile" -ForegroundColor White
Write-Host "⏱️  This will take ~15 seconds..." -ForegroundColor Yellow

# Run llava in background
$scriptBlock = {
    param($ImagePath, $Prompt, $OutputFile)
    
    $ollamaPath = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
    $output = & $ollamaPath run llava:latest $Prompt $ImagePath 2>&1
    
    # Clean output
    $cleaned = $output | Where-Object { $_ -notmatch '^\[' -and $_ -notmatch 'Added image' -and $_ -match '\S' } | Out-String
    
    $cleaned | Set-Content $OutputFile -Encoding UTF8
}

$job = Start-Job -ScriptBlock $scriptBlock -ArgumentList $ImagePath, $Prompt, $OutputFile

Write-Host "`n✅ Analysis started in background (Job ID: $($job.Id))" -ForegroundColor Green
Write-Host "`n📋 To check status:" -ForegroundColor Cyan
Write-Host "  Get-Job $($job.Id)" -ForegroundColor White
Write-Host "`n📖 To read result:" -ForegroundColor Cyan
Write-Host "  Get-Content '$OutputFile'" -ForegroundColor White
Write-Host "`n🎯 Or just wait and I'll show it:" -ForegroundColor Cyan

# Wait and show result
Wait-Job $job | Out-Null
$result = Get-Content $OutputFile

Write-Host "`n" + ("="*80) -ForegroundColor Green
Write-Host "✅ ANALYSIS COMPLETE" -ForegroundColor Green
Write-Host ("="*80) -ForegroundColor Green
Write-Host "`n$result`n"

Remove-Job $job

return @{
    "job_id" = $jobId
    "output_file" = $OutputFile
    "result" = $result
}
