@echo off
title ittybitty webapp
setlocal
set "ROOT=%~dp0"
set "WEBAPP=%ROOT%webapp\start.bat"
if not exist "%WEBAPP%" (
  echo [ERROR] Missing launcher: %WEBAPP%
  pause
  exit /b 1
)
call "%WEBAPP%" %*
exit /b %ERRORLEVEL%
