@echo off
REM Direkt client launcher - admin ister, goodbyedpi'yi sadece Discord icin acar
cd /d "%~dp0"
net session >nul 2>&1
if %errorlevel% neq 0 (
  echo Yonetici izni isteniyor...
  powershell -Command "Start-Process '%~f0' -Verb RunAs"
  exit /b
)
where python >nul 2>&1
if %errorlevel% neq 0 (
  echo HATA: python bulunamadi. python.org'dan kur.
  pause
  exit /b 1
)
python desktop_client.py
pause
