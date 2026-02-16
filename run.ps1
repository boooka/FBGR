# Запуск API FBGR (Django). Перед первым запуском: pip install -r requirements.txt
# Grafana: установите плагин Infinity и добавьте источник с URL http://localhost:8000

$host.UI.RawUI.WindowTitle = "FBGR API"
Set-Location $PSScriptRoot
Write-Host "FBGR API: http://127.0.0.1:8000/api/" -ForegroundColor Green
Write-Host "  health:  /api/health/" -ForegroundColor Gray
Write-Host "  MP:      /api/mp/orders/count/?dt_from=2024-01-01&dt_to=2024-12-31" -ForegroundColor Gray
Write-Host "  Ozon:    /api/mp/ozon_goods/count/" -ForegroundColor Gray
Write-Host ""
python manage.py runserver
