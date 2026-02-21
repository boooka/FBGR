# Запуск моста FBGR (32-bit Python + 32-bit Firebird).
# Используйте, когда основное приложение — 64-bit и задано FIREBIRD_BRIDGE_URL.
# Перед запуском: создайте venv 32-bit Python (py -3.12-32 -m venv .venv32), активируйте и pip install -r requirements.txt.
# В .env моста НЕ задавайте FIREBIRD_BRIDGE_URL.

$host.UI.RawUI.WindowTitle = "FBGR Bridge (32-bit)"
Set-Location $PSScriptRoot
$port = 8765
Write-Host "FBGR Bridge: http://127.0.0.1:$port/api/" -ForegroundColor Green
Write-Host "  (для основного приложения задайте FIREBIRD_BRIDGE_URL=http://127.0.0.1:$port)" -ForegroundColor Gray
Write-Host ""
python manage.py runserver $port
