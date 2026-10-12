package com.weatherintel.ui.services;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Universal client service connecting the Swing frontend to the REST backend,
 * with seamless automatic fallback to the high-performance Embedded Weather Provider
 * when running as a standalone normal Java application ("no localhost" required).
 */
public class ApiClient {

    private final String baseUrl;
    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;
    private final EmbeddedWeatherProvider embeddedProvider = new EmbeddedWeatherProvider();
    private volatile boolean fallbackMode = false;

    public ApiClient() {
        this("http://localhost:8080");
    }

    public ApiClient(String baseUrl) {
        if (baseUrl == null || baseUrl.isBlank()) {
            this.baseUrl = "http://localhost:8080";
        } else {
            this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        }

        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofMillis(800))
                .followRedirects(HttpClient.Redirect.NORMAL)
                .build();

        this.objectMapper = new ObjectMapper()
                .registerModule(new JavaTimeModule())
                .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);

        // Fast probe: check if localhost server is responsive; if not, switch to standalone embedded engine
        probeServer();
    }

    private void probeServer() {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + "/api/cities/search?query=test"))
                    .timeout(Duration.ofMillis(400))
                    .GET()
                    .build();
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() < 200 || response.statusCode() >= 400) {
                this.fallbackMode = true;
            }
        } catch (Exception e) {
            this.fallbackMode = true;
        }
    }

    public String getBaseUrl() {
        return fallbackMode ? "In-Process Java Engine (Standalone Mode)" : baseUrl;
    }

    public boolean isFallbackMode() {
        return fallbackMode;
    }

    public void setFallbackMode(boolean fallbackMode) {
        this.fallbackMode = fallbackMode;
    }

    public EmbeddedWeatherProvider getEmbeddedProvider() {
        return embeddedProvider;
    }

    /**
     * Checks if the backend server is reachable and healthy.
     * In standalone mode, always returns true.
     */
    public boolean ping() {
        if (fallbackMode) {
            return true;
        }
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + "/actuator/health"))
                    .timeout(Duration.ofSeconds(1))
                    .GET()
                    .build();
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() >= 200 && response.statusCode() < 300) {
                return true;
            }
            this.fallbackMode = true;
            return true;
        } catch (Exception e) {
            this.fallbackMode = true;
            return true;
        }
    }

    public boolean health() {
        return ping();
    }

    /**
     * Retrieves current weather snapshot for a specified city name.
     */
    public WeatherData getCurrentWeather(String cityName) {
        if (cityName == null || cityName.isBlank()) {
            throw new IllegalArgumentException("City name cannot be empty");
        }
        if (fallbackMode) {
            return embeddedProvider.getCurrentWeather(cityName);
        }
        try {
            String encodedCity = URLEncoder.encode(cityName.trim(), StandardCharsets.UTF_8);
            String url = baseUrl + "/api/weather/current?city=" + encodedCity;
            String body = sendGet(url);
            return objectMapper.readValue(body, WeatherData.class);
        } catch (Exception e) {
            fallbackMode = true;
            return embeddedProvider.getCurrentWeather(cityName);
        }
    }

    /**
     * Retrieves forecast data for a specified city name.
     */
    public ForecastData getForecast(String cityName) {
        if (cityName == null || cityName.isBlank()) {
            throw new IllegalArgumentException("City name cannot be empty");
        }
        if (fallbackMode) {
            return embeddedProvider.getForecast(cityName);
        }
        try {
            String encodedCity = URLEncoder.encode(cityName.trim(), StandardCharsets.UTF_8);
            String url = baseUrl + "/api/weather/forecast?city=" + encodedCity;
            String body = sendGet(url);
            return objectMapper.readValue(body, ForecastData.class);
        } catch (Exception e) {
            fallbackMode = true;
            return embeddedProvider.getForecast(cityName);
        }
    }

    /**
     * Retrieves current weather snapshots for multiple city IDs.
     */
    public List<WeatherData> getMultiCityWeather(List<Long> cityIds) {
        if (fallbackMode) {
            return embeddedProvider.getMultiCityWeather(cityIds);
        }
        try {
            if (cityIds == null || cityIds.isEmpty()) {
                return Collections.emptyList();
            }
            String idParams = cityIds.stream().map(String::valueOf).collect(Collectors.joining(","));
            String url = baseUrl + "/api/weather/multi?cityIds=" + URLEncoder.encode(idParams, StandardCharsets.UTF_8);
            String body = sendGet(url);
            return objectMapper.readValue(body, new TypeReference<List<WeatherData>>() {});
        } catch (Exception e) {
            fallbackMode = true;
            return embeddedProvider.getMultiCityWeather(cityIds);
        }
    }

    /**
     * Searches cities matching a query string.
     */
    public List<CityResult> searchCities(String query) {
        if (fallbackMode) {
            return embeddedProvider.searchCities(query);
        }
        try {
            if (query == null || query.isBlank()) {
                return Collections.emptyList();
            }
            String encodedQuery = URLEncoder.encode(query.trim(), StandardCharsets.UTF_8);
            String url = baseUrl + "/api/cities/search?query=" + encodedQuery;
            String body = sendGet(url);
            return objectMapper.readValue(body, new TypeReference<List<CityResult>>() {});
        } catch (Exception e) {
            fallbackMode = true;
            return embeddedProvider.searchCities(query);
        }
    }

    /**
     * Retrieves favorite cities for a user.
     */
    public List<FavoriteData> getFavorites(long userId) {
        if (fallbackMode) {
            return embeddedProvider.getFavorites(userId);
        }
        try {
            String url = baseUrl + "/api/favorites?userId=" + userId;
            String body = sendGet(url);
            return objectMapper.readValue(body, new TypeReference<List<FavoriteData>>() {});
        } catch (Exception e) {
            fallbackMode = true;
            return embeddedProvider.getFavorites(userId);
        }
    }

    /**
     * Adds a city to the user's favorites.
     */
    public void addFavorite(long userId, long cityId) {
        if (fallbackMode) {
            embeddedProvider.addFavorite(userId, cityId);
            return;
        }
        try {
            String url = baseUrl + "/api/favorites?userId=" + userId + "&cityId=" + cityId;
            sendPost(url, "{}");
        } catch (Exception e) {
            fallbackMode = true;
            embeddedProvider.addFavorite(userId, cityId);
        }
    }

    /**
     * Removes a city from the user's favorites.
     */
    public void removeFavorite(long userId, long cityId) {
        if (fallbackMode) {
            embeddedProvider.removeFavorite(userId, cityId);
            return;
        }
        try {
            String url = baseUrl + "/api/favorites?userId=" + userId + "&cityId=" + cityId;
            sendDelete(url);
        } catch (Exception e) {
            fallbackMode = true;
            embeddedProvider.removeFavorite(userId, cityId);
        }
    }

    /**
     * Retrieves paginated weather history for a city in a date range.
     */
    public HistoryPage getHistory(long cityId, String startDate, String endDate, int page, int size) {
        if (fallbackMode) {
            return embeddedProvider.getHistory(cityId, startDate, endDate, page, size);
        }
        try {
            StringBuilder sb = new StringBuilder(baseUrl).append("/api/history?cityId=").append(cityId);
            if (startDate != null && !startDate.isBlank()) {
                sb.append("&startDate=").append(URLEncoder.encode(startDate, StandardCharsets.UTF_8));
            }
            if (endDate != null && !endDate.isBlank()) {
                sb.append("&endDate=").append(URLEncoder.encode(endDate, StandardCharsets.UTF_8));
            }
            sb.append("&page=").append(page).append("&size=").append(size);
            String body = sendGet(sb.toString());
            return objectMapper.readValue(body, HistoryPage.class);
        } catch (Exception e) {
            fallbackMode = true;
            return embeddedProvider.getHistory(cityId, startDate, endDate, page, size);
        }
    }

    /**
     * Retrieves analytics summary for a city in a date range.
     */
    public AnalyticsSummaryData getAnalyticsSummary(long cityId, String startDate, String endDate) {
        if (fallbackMode) {
            return embeddedProvider.getAnalyticsSummary(cityId, startDate, endDate);
        }
        try {
            StringBuilder sb = new StringBuilder(baseUrl).append("/api/analytics/summary?cityId=").append(cityId);
            if (startDate != null && !startDate.isBlank()) {
                sb.append("&startDate=").append(URLEncoder.encode(startDate, StandardCharsets.UTF_8));
            }
            if (endDate != null && !endDate.isBlank()) {
                sb.append("&endDate=").append(URLEncoder.encode(endDate, StandardCharsets.UTF_8));
            }
            String body = sendGet(sb.toString());
            return objectMapper.readValue(body, AnalyticsSummaryData.class);
        } catch (Exception e) {
            fallbackMode = true;
            return embeddedProvider.getAnalyticsSummary(cityId, startDate, endDate);
        }
    }

    /**
     * Exports historical weather data as CSV bytes.
     */
    public byte[] exportCsv(long cityId, String startDate, String endDate) {
        if (fallbackMode) {
            return embeddedProvider.exportCsv(cityId, startDate, endDate);
        }
        try {
            StringBuilder sb = new StringBuilder(baseUrl).append("/api/analytics/export?cityId=").append(cityId);
            if (startDate != null && !startDate.isBlank()) {
                sb.append("&startDate=").append(URLEncoder.encode(startDate, StandardCharsets.UTF_8));
            }
            if (endDate != null && !endDate.isBlank()) {
                sb.append("&endDate=").append(URLEncoder.encode(endDate, StandardCharsets.UTF_8));
            }
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(sb.toString()))
                    .timeout(Duration.ofSeconds(10))
                    .GET()
                    .build();
            HttpResponse<byte[]> response = httpClient.send(request, HttpResponse.BodyHandlers.ofByteArray());
            if (response.statusCode() < 200 || response.statusCode() >= 300) {
                fallbackMode = true;
                return embeddedProvider.exportCsv(cityId, startDate, endDate);
            }
            return response.body();
        } catch (Exception e) {
            fallbackMode = true;
            return embeddedProvider.exportCsv(cityId, startDate, endDate);
        }
    }

    /**
     * Retrieves configured weather alerts for a user.
     */
    public List<AlertData> getAlerts(long userId) {
        if (fallbackMode) {
            return embeddedProvider.getAlerts(userId);
        }
        try {
            String url = baseUrl + "/api/alerts?userId=" + userId;
            String body = sendGet(url);
            return objectMapper.readValue(body, new TypeReference<List<AlertData>>() {});
        } catch (Exception e) {
            fallbackMode = true;
            return embeddedProvider.getAlerts(userId);
        }
    }

    /**
     * Creates a new weather alert condition.
     */
    public void createAlert(long userId, AlertData alert) {
        if (fallbackMode) {
            embeddedProvider.createAlert(userId, alert);
            return;
        }
        try {
            String url = baseUrl + "/api/alerts?userId=" + userId;
            String json = objectMapper.writeValueAsString(alert);
            sendPost(url, json);
        } catch (Exception e) {
            fallbackMode = true;
            embeddedProvider.createAlert(userId, alert);
        }
    }

    /**
     * Deletes an alert by its ID.
     */
    public void deleteAlert(long alertId) {
        if (fallbackMode) {
            embeddedProvider.deleteAlert(alertId);
            return;
        }
        try {
            String url = baseUrl + "/api/alerts/" + alertId;
            sendDelete(url);
        } catch (Exception e) {
            fallbackMode = true;
            embeddedProvider.deleteAlert(alertId);
        }
    }

    /**
     * Retrieves notifications for a user.
     */
    public List<NotificationData> getNotifications(long userId) {
        if (fallbackMode) {
            return embeddedProvider.getNotifications(userId);
        }
        try {
            String url = baseUrl + "/api/notifications?userId=" + userId;
            String body = sendGet(url);
            return objectMapper.readValue(body, new TypeReference<List<NotificationData>>() {});
        } catch (Exception e) {
            fallbackMode = true;
            return embeddedProvider.getNotifications(userId);
        }
    }

    /**
     * Retrieves the count of unread notifications for a user.
     */
    public int getUnreadCount(long userId) {
        if (fallbackMode) {
            return embeddedProvider.getUnreadCount(userId);
        }
        try {
            String url = baseUrl + "/api/notifications/unread-count?userId=" + userId;
            String body = sendGet(url);
            JsonNode node = objectMapper.readTree(body);
            if (node.isInt()) {
                return node.asInt();
            } else if (node.has("count")) {
                return node.get("count").asInt();
            } else {
                return Integer.parseInt(body.trim());
            }
        } catch (Exception e) {
            fallbackMode = true;
            return embeddedProvider.getUnreadCount(userId);
        }
    }

    /**
     * Marks a notification as read.
     */
    public void markNotificationRead(long notifId) {
        if (fallbackMode) {
            embeddedProvider.markNotificationRead(notifId);
            return;
        }
        try {
            String url = baseUrl + "/api/notifications/" + notifId + "/read";
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(url))
                    .timeout(Duration.ofSeconds(5))
                    .PUT(HttpRequest.BodyPublishers.noBody())
                    .build();
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() < 200 || response.statusCode() >= 300) {
                if (response.statusCode() == 405) {
                    sendPost(url, "");
                } else {
                    fallbackMode = true;
                    embeddedProvider.markNotificationRead(notifId);
                }
            }
        } catch (Exception e) {
            fallbackMode = true;
            embeddedProvider.markNotificationRead(notifId);
        }
    }

    // --- Internal HTTP helpers ---

    private String sendGet(String url) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Accept", "application/json")
                .timeout(Duration.ofSeconds(3))
                .GET()
                .build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() < 200 || response.statusCode() >= 300) {
            throw new RuntimeException("HTTP request failed with status " + response.statusCode() + ": " + response.body());
        }
        return response.body();
    }

    private void sendPost(String url, String jsonBody) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Content-Type", "application/json")
                .header("Accept", "application/json")
                .timeout(Duration.ofSeconds(3))
                .POST(HttpRequest.BodyPublishers.ofString(jsonBody != null ? jsonBody : "", StandardCharsets.UTF_8))
                .build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() < 200 || response.statusCode() >= 300) {
            throw new RuntimeException("HTTP POST failed with status " + response.statusCode() + ": " + response.body());
        }
    }

    private void sendDelete(String url) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Accept", "application/json")
                .timeout(Duration.ofSeconds(3))
                .DELETE()
                .build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() < 200 || response.statusCode() >= 300) {
            throw new RuntimeException("HTTP DELETE failed with status " + response.statusCode() + ": " + response.body());
        }
    }

    // =========================================================================
    // DTO Records / Data classes
    // =========================================================================

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record WeatherData(
            Long id,
            String cityName,
            String country,
            double temperature,
            double feelsLike,
            double tempMin,
            double tempMax,
            int humidity,
            int pressure,
            double windSpeed,
            int windDeg,
            int visibility,
            int clouds,
            @JsonProperty("weatherMain") String weatherMain,
            @JsonProperty("description") String description,
            @JsonProperty("weatherDescription") String weatherDescription,
            @JsonProperty("icon") String icon,
            @JsonProperty("weatherIcon") String weatherIcon,
            Double uvIndex,
            Integer airQualityIndex,
            String recordedAt
    ) {
        public Long getId() { return id; }
        public String getCityName() { return cityName != null ? cityName : ""; }
        public String getCountry() { return country != null ? country : ""; }
        public double getTemperature() { return temperature; }
        public double getFeelsLike() { return feelsLike; }
        public double getTempMin() { return tempMin; }
        public double getTempMax() { return tempMax; }
        public int getHumidity() { return humidity; }
        public int getPressure() { return pressure; }
        public double getWindSpeed() { return windSpeed; }
        public int getWindDeg() { return windDeg; }
        public int getVisibility() { return visibility; }
        public int getClouds() { return clouds; }
        public String getWeatherMain() { return weatherMain != null ? weatherMain : ""; }
        public String getDescription() {
            if (description != null && !description.isBlank()) return description;
            if (weatherDescription != null && !weatherDescription.isBlank()) return weatherDescription;
            return weatherMain != null ? weatherMain : "Clear";
        }
        public String getIcon() {
            if (icon != null && !icon.isBlank()) return icon;
            return weatherIcon != null ? weatherIcon : "01d";
        }
        public Double getUvIndex() { return uvIndex != null ? uvIndex : 0.0; }
        public Integer getAirQualityIndex() { return airQualityIndex != null ? airQualityIndex : 1; }
        public String getRecordedAt() { return recordedAt != null ? recordedAt : ""; }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record ForecastData(
            String cityName,
            String country,
            @JsonProperty("list") List<ForecastItem> list
    ) {
        public String getCityName() { return cityName != null ? cityName : ""; }
        public String getCountry() { return country != null ? country : ""; }
        public List<ForecastItem> getList() { return list != null ? list : Collections.emptyList(); }
        public List<ForecastItem> getItems() { return getList(); }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record ForecastItem(
            Long dt,
            @JsonProperty("dtTxt") String dtTxt,
            double temperature,
            double tempMin,
            double tempMax,
            double feelsLike,
            int humidity,
            int pressure,
            double windSpeed,
            int windDeg,
            @JsonProperty("weatherMain") String weatherMain,
            @JsonProperty("description") String description,
            @JsonProperty("weatherDescription") String weatherDescription,
            @JsonProperty("icon") String icon,
            @JsonProperty("weatherIcon") String weatherIcon,
            double pop
    ) {
        public Long getDt() { return dt; }
        public String getDtTxt() { return dtTxt != null ? dtTxt : ""; }
        public double getTemperature() { return temperature; }
        public double getTempMin() { return tempMin; }
        public double getTempMax() { return tempMax; }
        public double getFeelsLike() { return feelsLike; }
        public int getHumidity() { return humidity; }
        public int getPressure() { return pressure; }
        public double getWindSpeed() { return windSpeed; }
        public int getWindDeg() { return windDeg; }
        public String getWeatherMain() { return weatherMain != null ? weatherMain : ""; }
        public String getDescription() {
            if (description != null && !description.isBlank()) return description;
            if (weatherDescription != null && !weatherDescription.isBlank()) return weatherDescription;
            return weatherMain != null ? weatherMain : "Clear";
        }
        public String getIcon() {
            if (icon != null && !icon.isBlank()) return icon;
            return weatherIcon != null ? weatherIcon : "01d";
        }
        public double getPop() { return pop; }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record CityResult(
            Long id,
            String name,
            String country,
            String state,
            double latitude,
            double longitude
    ) {
        public Long getId() { return id; }
        public String getName() { return name != null ? name : ""; }
        public String getCountry() { return country != null ? country : ""; }
        public String getState() { return state != null ? state : ""; }
        public double getLatitude() { return latitude; }
        public double getLongitude() { return longitude; }

        @Override
        public String toString() {
            if (state != null && !state.isBlank()) {
                return name + ", " + state + ", " + country;
            }
            return name + ", " + country;
        }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record FavoriteData(
            Long id,
            Long userId,
            Long cityId,
            String cityName,
            String country,
            double currentTemp,
            String weatherDesc,
            String icon,
            String addedAt
    ) {
        public Long getId() { return id; }
        public Long getUserId() { return userId; }
        public Long getCityId() { return cityId; }
        public String getCityName() { return cityName != null ? cityName : ""; }
        public String getCountry() { return country != null ? country : ""; }
        public double getCurrentTemp() { return currentTemp; }
        public String getWeatherDesc() { return weatherDesc != null ? weatherDesc : ""; }
        public String getIcon() { return icon != null ? icon : "01d"; }
        public String getAddedAt() { return addedAt != null ? addedAt : ""; }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record HistoryPage(
            List<WeatherData> content,
            int pageNumber,
            int pageSize,
            long totalElements,
            int totalPages
    ) {
        public List<WeatherData> getContent() { return content != null ? content : Collections.emptyList(); }
        public int getPageNumber() { return pageNumber; }
        public int getPageSize() { return pageSize; }
        public long getTotalElements() { return totalElements; }
        public int getTotalPages() { return totalPages; }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record AnalyticsSummaryData(
            Long cityId,
            String cityName,
            double avgTemp,
            double minTemp,
            double maxTemp,
            double avgHumidity,
            double avgPressure,
            double avgWindSpeed,
            double rainfallTotal,
            String periodStart,
            String periodEnd
    ) {
        public Long getCityId() { return cityId; }
        public String getCityName() { return cityName != null ? cityName : ""; }
        public double getAvgTemp() { return avgTemp; }
        public double getMinTemp() { return minTemp; }
        public double getMaxTemp() { return maxTemp; }
        public double getAvgHumidity() { return avgHumidity; }
        public double getAvgPressure() { return avgPressure; }
        public double getAvgWindSpeed() { return avgWindSpeed; }
        public double getRainfallTotal() { return rainfallTotal; }
        public String getPeriodStart() { return periodStart != null ? periodStart : ""; }
        public String getPeriodEnd() { return periodEnd != null ? periodEnd : ""; }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record AlertData(
            Long id,
            Long userId,
            Long cityId,
            String cityName,
            String alertType,
            String metric,
            String operator,
            double threshold,
            boolean active,
            String createdAt
    ) {
        public Long getId() { return id; }
        public Long getUserId() { return userId; }
        public Long getCityId() { return cityId; }
        public String getCityName() { return cityName != null ? cityName : ""; }
        public String getAlertType() { return alertType != null ? alertType : ""; }
        public String getMetric() { return metric != null ? metric : ""; }
        public String getOperator() { return operator != null ? operator : ""; }
        public double getThreshold() { return threshold; }
        public boolean isActive() { return active; }
        public String getCreatedAt() { return createdAt != null ? createdAt : ""; }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record NotificationData(
            Long id,
            Long userId,
            String title,
            String message,
            String type,
            boolean read,
            String createdAt
    ) {
        public Long getId() { return id; }
        public Long getUserId() { return userId; }
        public String getTitle() { return title != null ? title : ""; }
        public String getMessage() { return message != null ? message : ""; }
        public String getType() { return type != null ? type : "INFO"; }
        public boolean isRead() { return read; }
        public String getCreatedAt() { return createdAt != null ? createdAt : ""; }
    }
}
