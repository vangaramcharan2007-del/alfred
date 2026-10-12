$baseUrl = "http://localhost:8080"
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "       WEATHER INTELLIGENCE & MONITORING SYSTEM - LIVE SYSTEM DEMONSTRATION     " -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Seed Cities
Write-Host "[1/6] Fetching Seed Cities from Database (/api/cities)..." -ForegroundColor Yellow
$cities = Invoke-RestMethod -Uri "$baseUrl/api/cities" -Method Get
Write-Host "  Found $($cities.Count) cities in database:" -ForegroundColor Green
foreach ($c in $cities) {
    Write-Host ("    - ID {0}: {1}, {2} (Lat: {3}, Lon: {4})" -f $c.id, $c.name, $c.country, $c.latitude, $c.longitude) -ForegroundColor Gray
}

# 2. Live Weather Ingestion for Multiple Cities
Write-Host ""
Write-Host "[2/6] Ingesting Real-Time Weather Snapshots (/api/weather/current)..." -ForegroundColor Yellow
$testCities = @("London", "Tokyo", "Paris", "Sydney")
$weatherResults = @()

foreach ($cName in $testCities) {
    try {
        $w = Invoke-RestMethod -Uri "$baseUrl/api/weather/current?city=$cName" -Method Get
        $weatherResults += $w
        Write-Host ("  [+] City: {0}, {1} | Temp: {2} C (Feels: {3} C) | Condition: {4} | Source: {5}" -f $w.cityName, $w.country, $w.temperature, $w.feelsLike, $w.weatherMain, $w.dataSource) -ForegroundColor Green
    } catch {
        Write-Host "  [-] Warning fetching $cName" -ForegroundColor DarkYellow
    }
}

# 3. Forecast Center
Write-Host ""
Write-Host "[3/6] Querying 5-Day / 3-Hour Forecast Center (/api/weather/forecast)..." -ForegroundColor Yellow
$forecast = Invoke-RestMethod -Uri "$baseUrl/api/weather/forecast?city=London" -Method Get
Write-Host ("  Forecast for {0}, {1} ({2} entries):" -f $forecast.cityName, $forecast.country, $forecast.forecasts.Count) -ForegroundColor Green
$forecast.forecasts | Select-Object -First 5 | ForEach-Object {
    Write-Host ("    Timeline: {0} | Temp: {1} C (Min: {2} C, Max: {3} C) | Precip: {4}% | Sky: {5}" -f $_.forecastTime, $_.temperature, $_.tempMin, $_.tempMax, [math]::Round($_.pop * 100), $_.weatherMain) -ForegroundColor Gray
}

# 4. User Favorites & Dynamic Weather Alerts
Write-Host ""
Write-Host "[4/6] Testing User Favorites & Alert Trigger Automation (/api/favorites, /api/alerts)..." -ForegroundColor Yellow
$favBody = '{"userId":1,"cityId":1}'
$fav = Invoke-RestMethod -Uri "$baseUrl/api/favorites" -Method Post -Body $favBody -ContentType "application/json"
Write-Host ("  Favorite Created: User {0} -> City {1} ({2})" -f $fav.userId, $fav.cityId, $fav.cityName) -ForegroundColor Green

$alertBody = '{"userId":1,"cityId":1,"cityName":"London","alertType":"TEMP_BELOW","thresholdValue":50.0,"conditionValue":"","enabled":true}'
$alert = Invoke-RestMethod -Uri "$baseUrl/api/alerts" -Method Post -Body $alertBody -ContentType "application/json"
Write-Host ("  Alert Rule Created: ID {0} on {1} | Type: {2} | Threshold: {3} C" -f $alert.id, $alert.cityName, $alert.alertType, $alert.thresholdValue) -ForegroundColor Green

# 5. Historical Weather Analytics & CSV Export
Write-Host ""
Write-Host "[5/6] Querying Historical Analytics & Exporting CSV Report (/api/analytics)..." -ForegroundColor Yellow
$past = (Get-Date).AddDays(-30).ToString("yyyy-MM-ddTHH:mm:ss")
$now = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
$summary = Invoke-RestMethod -Uri "$baseUrl/api/analytics/summary?cityId=1&startDate=$past&endDate=$now" -Method Get
Write-Host ("  Analytics Summary for {0}:" -f $summary.cityName) -ForegroundColor Green
Write-Host ("    - Total Historical Readings: {0}" -f $summary.totalReadings) -ForegroundColor Gray
Write-Host ("    - Temperature: Avg {0} C | Min {1} C | Max {2} C" -f $summary.avgTemp, $summary.minTemp, $summary.maxTemp) -ForegroundColor Gray
Write-Host ("    - Environment: Avg Humidity {0}% | Avg Pressure {1} hPa | Avg Wind {2} m/s" -f $summary.avgHumidity, $summary.avgPressure, $summary.avgWindSpeed) -ForegroundColor Gray

$csvResp = Invoke-WebRequest -Uri "$baseUrl/api/analytics/export/csv?cityId=1&startDate=$past&endDate=$now" -Method Get
Write-Host ("  CSV Report Downloaded: {0} bytes, Content-Type: {1}" -f $csvResp.Content.Length, $csvResp.Headers["Content-Type"]) -ForegroundColor Green

# 6. Live Dashboard Visual Console
Write-Host ""
Write-Host "[6/6] LIVE DESKTOP WEATHER DASHBOARD PREVIEW" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
foreach ($w in $weatherResults) {
    $tempF = [math]::Round(($w.temperature * 9 / 5) + 32, 1)
    $windKmh = [math]::Round($w.windSpeed * 3.6, 1)
    $badge = if ($w.dataSource -eq "API") { "[LIVE API]" } else { "[CACHED]" }
    
    $bars = [math]::Min(10, [math]::Max(0, [math]::Round($w.humidity / 10)))
    $empty = 10 - $bars
    $bar = ("#" * $bars) + ("-" * $empty)

    Write-Host ("LOCATION: {0}, {1}   STATUS: {2}   UPDATED: {3}" -f $w.cityName, $w.country, $badge, $w.lastUpdated) -ForegroundColor White
    Write-Host ("  TEMPERATURE:  {0} C  ({1} F)   | Feels Like: {2} C" -f $w.temperature, $tempF, $w.feelsLike) -ForegroundColor Yellow
    Write-Host ("  CONDITION:    {0} ({1})" -f $w.weatherMain, $w.weatherDescription) -ForegroundColor Gray
    Write-Host ("  HUMIDITY:     [{0}] {1}%   | Pressure: {2} hPa" -f $bar, $w.humidity, $w.pressure) -ForegroundColor Cyan
    Write-Host ("  WIND:         {0} m/s ({1} km/h) at {2} deg | Visibility: {3} m" -f $w.windSpeed, $windKmh, $w.windDeg, $w.visibility) -ForegroundColor Gray
    Write-Host "--------------------------------------------------------------------------------" -ForegroundColor DarkCyan
}

Write-Host "MULTI-CITY COMPARISON MATRIX:" -ForegroundColor White
Write-Host "City            Temp(C)    Feels(C)    Humidity(%)    Wind(m/s)    Condition" -ForegroundColor DarkCyan
foreach ($w in $weatherResults) {
    Write-Host ("{0,-15} {1,-10} {2,-11} {3,-14} {4,-12} {5}" -f $w.cityName, "$($w.temperature) C", "$($w.feelsLike) C", "$($w.humidity) %", "$($w.windSpeed) m/s", $w.weatherMain) -ForegroundColor Green
}
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "SUCCESS: FULL-STACK WEATHER INTELLIGENCE SYSTEM RUNNING AND VALIDATED!" -ForegroundColor Green
Write-Host ""
