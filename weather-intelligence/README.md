# Weather Intelligence & Monitoring System

A comprehensive, full-stack Advanced Object-Oriented Programming (AOOP) application featuring a professional **Java Swing** desktop UI, **Spring Boot** backend services, real-time WebSocket communication, embedded in-process weather processing engine, statistical analytics, and multi-city monitoring.

---

## Architecture Overview

```
+---------------------------------------------------------------------------------------+
|                               JAVA SWING DESKTOP UI                                   |
|  (WeatherApp, DashboardPanel, ForecastPanel, MultiCityPanel, HistoricalPanel, Alerts) |
+---------------------------------------------------------------------------------------+
            |                                                       |
            | (Fallback / Direct Mode)                              | (REST / WebSocket Mode)
            v                                                       v
+--------------------------------------+      +-----------------------------------------+
|     Embedded Weather Provider        |      |       Spring Boot 3 REST / WebSocket    |
|  - In-Process Real-time Engine       |      |  - 6 Controllers, 8 Services, 8 Repos   |
|  - Direct OpenWeather HTTPS Client   |      |  - WebSocket Publisher & Scheduled Jobs |
|  - In-Memory Persistence & Analytics |      |  - JPA/Hibernate + H2/MySQL Database    |
+--------------------------------------+      +-----------------------------------------+
```

### Key Modules

1. **`weather-frontend`**:
   - Modern Java Swing desktop application styled with FlatLaf Dark theme.
   - 6 functional tabs:
     - **Dashboard**: Real-time temperature, feels-like, humidity, pressure, wind direction/speed, cloud cover, visibility, unit toggles (°C/°F, km/h, mph, knots).
     - **Forecast Center**: 5-day / 3-hour forecast table and hourly trend projections.
     - **Multi-City Monitoring**: Favorite city management, search, comparative analytics matrix.
     - **Historical Analytics**: Statistical summaries (min, max, avg, pressure, humidity), JFreeChart charts, and CSV report export.
     - **Alerts & Notifications**: Configurable threshold rules and live notifications feed.
     - **Settings**: Refresh intervals, unit preferences, and API configuration.
   - Dual-Mode `ApiClient`: Seamlessly runs in **Standalone Normal Java Mode** (no localhost server needed) using the in-process `EmbeddedWeatherProvider`, or connects to a remote/local Spring Boot backend.

2. **`weather-backend`**:
   - Spring Boot 3 enterprise backend.
   - 8 JPA Entities: `User`, `City`, `FavoriteCity`, `WeatherSnapshot`, `ForecastEntry`, `AlertRule`, `Notification`, `AuditRecord`.
   - 8 Repositories with custom JPQL queries for date-range analytics and city lookups.
   - Centralized validation, Bean Validation (`@Valid`), global error handler (`@ControllerAdvice`), and security configuration.
   - STOMP/WebSocket broker for real-time broadcast of meteorological alerts and snapshots.

---

## Quick Start (Normal Standalone Java - No Localhost Required)

### 1. Launch the Desktop Swing GUI Application
Double-click or run:
```bat
.\run-app.bat
```
Or with Java directly:
```bash
java -jar weather-frontend\target\weather-frontend-1.0.0.jar
```

### 2. Run the Live Console Demonstration
```bat
.\run-demo.bat
```
Or via java classpath:
```bash
java -cp "weather-frontend\target\weather-frontend-1.0.0.jar;weather-frontend\target\lib\*" com.weatherintel.ui.StandaloneDemo
```

---

## Optional: Running Full Distributed Client-Server Stack

If you wish to run the separate Spring Boot backend on localhost:

### 1. Start the Spring Boot Backend
```bash
java -jar weather-backend\target\weather-backend-1.0.0.jar
```
Backend will start on `http://localhost:8080`.

### 2. Launch the Desktop Client
```bash
java -jar weather-frontend\target\weather-frontend-1.0.0.jar
```
The desktop client will automatically detect the localhost backend and connect over HTTP REST and WebSocket!

---

## Live OpenWeather API Integration (Optional)

To connect directly to live satellite OpenWeather data:
1. Set the environment variable:
   ```powershell
   $env:OPENWEATHER_API_KEY = "your_actual_api_key_here"
   ```
2. Launch the application. The system will automatically fetch live weather conditions from OpenWeather over HTTPS. If no key is set or offline, it uses its realistic simulation model.

---

## Building and Testing

### Build with Maven
```bash
mvn clean package -DskipTests
```

### Run All Unit & Integration Tests
```bash
mvn test
```
All tests across backend and frontend are automated with JUnit 5 and Mockito.
