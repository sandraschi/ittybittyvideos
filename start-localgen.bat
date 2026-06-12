@echo off
title LocalGen sidecar (Wan 2.2)
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start_localgen.ps1" %*
pause
