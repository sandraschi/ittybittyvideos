# Prepend a known FFmpeg install when ffmpeg/ffprobe are not on PATH (common on Windows).
if (Get-Command ffmpeg -ErrorAction SilentlyContinue) {
    return
}

$candidates = @(
    "C:\ffmpeg\bin",
    "$env:LOCALAPPDATA\Microsoft\WinGet\Links",
    "$env:ProgramFiles\ffmpeg\bin"
)

foreach ($dir in $candidates) {
    $exe = Join-Path $dir "ffmpeg.exe"
    if (Test-Path $exe) {
        $env:Path = "$dir;$env:Path"
        break
    }
}
