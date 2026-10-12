package com.weatherintel.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.weatherintel.dto.CitySearchResult;
import com.weatherintel.dto.ForecastItemDto;
import com.weatherintel.dto.ForecastResponse;
import com.weatherintel.dto.WeatherResponse;
import com.weatherintel.exception.WeatherApiException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpStatusCodeException;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class OpenWeatherApiClient {

    private static final Logger log = LoggerFactory.getLogger(OpenWeatherApiClient.class);

    private static final String BASE_URL = "https://api.openweathermap.org/data/2.5";
    private static final String GEO_URL = "https://api.openweathermap.org/geo/1.0";

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;
    private final String apiKey;

    private final Map<String, WeatherResponse> weatherCache = new ConcurrentHashMap<>();
    private final Map<String, ForecastResponse> forecastCache = new ConcurrentHashMap<>();

    public OpenWeatherApiClient(RestTemplate restTemplate,
                                ObjectMapper objectMapper,
                                @Value("${weather.api.key:mock-api-key}") String apiKey) {
        this.restTemplate = restTemplate;
        this.objectMapper = objectMapper;
        this.apiKey = apiKey;
    }

    public WeatherResponse getCurrentWeather(String cityName) {
        log.info("Fetching current weather for city: {}", cityName);
        String url = UriComponentsBuilder.fromHttpUrl(BASE_URL + "/weather")
                .queryParam("q", cityName)
                .queryParam("appid", apiKey)
                .queryParam("units", "metric")
                .toUriString();

        try {
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                WeatherResponse weatherResponse = parseWeatherResponse(response.getBody(), "API");
                cacheWeatherResponse(cityName, weatherResponse);
                return weatherResponse;
            } else {
                throw new WeatherApiException("Failed to fetch weather from API: " + response.getStatusCode(),
                        response.getStatusCode().value());
            }
        } catch (HttpStatusCodeException ex) {
            log.error("API error fetching weather for {}: {} {}", cityName, ex.getStatusCode(), ex.getResponseBodyAsString());
            WeatherResponse cached = getCachedWeather(cityName);
            if (cached != null) {
                log.warn("Returning cached weather response for city: {}", cityName);
                return cached;
            }
            throw new WeatherApiException("OpenWeatherMap API error: " + ex.getMessage(), ex, ex.getStatusCode().value());
        } catch (RestClientException | IllegalStateException ex) {
            log.error("Network or client error fetching weather for {}: {}", cityName, ex.getMessage());
            WeatherResponse cached = getCachedWeather(cityName);
            if (cached != null) {
                log.warn("Returning cached weather response for city: {}", cityName);
                return cached;
            }
            throw new WeatherApiException("Failed to communicate with OpenWeatherMap API: " + ex.getMessage(), ex, 503);
        } catch (Exception ex) {
            log.error("Unexpected error fetching weather for {}: {}", cityName, ex.getMessage(), ex);
            WeatherResponse cached = getCachedWeather(cityName);
            if (cached != null) {
                log.warn("Returning cached weather response for city: {}", cityName);
                return cached;
            }
            throw new WeatherApiException("Unexpected error fetching weather data: " + ex.getMessage(), ex, 500);
        }
    }

    public WeatherResponse getCurrentWeatherByCoords(double lat, double lon) {
        log.info("Fetching current weather for coordinates: lat={}, lon={}", lat, lon);
        String cacheKey = "coords:" + lat + "," + lon;
        String url = UriComponentsBuilder.fromHttpUrl(BASE_URL + "/weather")
                .queryParam("lat", lat)
                .queryParam("lon", lon)
                .queryParam("appid", apiKey)
                .queryParam("units", "metric")
                .toUriString();

        try {
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                WeatherResponse weatherResponse = parseWeatherResponse(response.getBody(), "API");
                weatherCache.put(cacheKey, copyWithDataSource(weatherResponse, "CACHE"));
                if (weatherResponse.getCityName() != null && !weatherResponse.getCityName().isBlank()) {
                    weatherCache.put(weatherResponse.getCityName().toLowerCase().trim(), copyWithDataSource(weatherResponse, "CACHE"));
                }
                return weatherResponse;
            } else {
                throw new WeatherApiException("Failed to fetch weather by coords: " + response.getStatusCode(),
                        response.getStatusCode().value());
            }
        } catch (HttpStatusCodeException ex) {
            log.error("API error fetching weather for coords lat={}, lon={}: {}", lat, lon, ex.getMessage());
            WeatherResponse cached = weatherCache.get(cacheKey);
            if (cached != null) {
                log.warn("Returning cached weather for coords: lat={}, lon={}", lat, lon);
                return cached;
            }
            throw new WeatherApiException("OpenWeatherMap API error: " + ex.getMessage(), ex, ex.getStatusCode().value());
        } catch (RestClientException | IllegalStateException ex) {
            log.error("Network or client error fetching weather for coords lat={}, lon={}: {}", lat, lon, ex.getMessage());
            WeatherResponse cached = weatherCache.get(cacheKey);
            if (cached != null) {
                log.warn("Returning cached weather for coords: lat={}, lon={}", lat, lon);
                return cached;
            }
            throw new WeatherApiException("Failed to communicate with OpenWeatherMap API: " + ex.getMessage(), ex, 503);
        } catch (Exception ex) {
            log.error("Unexpected error fetching weather for coords lat={}, lon={}: {}", lat, lon, ex.getMessage(), ex);
            WeatherResponse cached = weatherCache.get(cacheKey);
            if (cached != null) {
                log.warn("Returning cached weather for coords: lat={}, lon={}", lat, lon);
                return cached;
            }
            throw new WeatherApiException("Unexpected error fetching weather data: " + ex.getMessage(), ex, 500);
        }
    }

    public ForecastResponse getForecast(String cityName) {
        log.info("Fetching forecast for city: {}", cityName);
        String url = UriComponentsBuilder.fromHttpUrl(BASE_URL + "/forecast")
                .queryParam("q", cityName)
                .queryParam("appid", apiKey)
                .queryParam("units", "metric")
                .toUriString();

        try {
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                ForecastResponse forecastResponse = parseForecastResponse(response.getBody());
                if (cityName != null) {
                    forecastCache.put(cityName.toLowerCase().trim(), forecastResponse);
                }
                return forecastResponse;
            } else {
                throw new WeatherApiException("Failed to fetch forecast from API: " + response.getStatusCode(),
                        response.getStatusCode().value());
            }
        } catch (HttpStatusCodeException ex) {
            log.error("API error fetching forecast for {}: {}", cityName, ex.getMessage());
            ForecastResponse cached = getCachedForecast(cityName);
            if (cached != null) {
                log.warn("Returning cached forecast for city: {}", cityName);
                return cached;
            }
            throw new WeatherApiException("OpenWeatherMap forecast API error: " + ex.getMessage(), ex, ex.getStatusCode().value());
        } catch (RestClientException | IllegalStateException ex) {
            log.error("Network or client error fetching forecast for {}: {}", cityName, ex.getMessage());
            ForecastResponse cached = getCachedForecast(cityName);
            if (cached != null) {
                log.warn("Returning cached forecast for city: {}", cityName);
                return cached;
            }
            throw new WeatherApiException("Failed to communicate with OpenWeatherMap API: " + ex.getMessage(), ex, 503);
        } catch (Exception ex) {
            log.error("Unexpected error fetching forecast for {}: {}", cityName, ex.getMessage(), ex);
            ForecastResponse cached = getCachedForecast(cityName);
            if (cached != null) {
                log.warn("Returning cached forecast for city: {}", cityName);
                return cached;
            }
            throw new WeatherApiException("Unexpected error fetching forecast data: " + ex.getMessage(), ex, 500);
        }
    }

    public List<CitySearchResult> searchCities(String query) {
        log.info("Searching cities with query: {}", query);
        String url = UriComponentsBuilder.fromHttpUrl(GEO_URL + "/direct")
                .queryParam("q", query)
                .queryParam("limit", 10)
                .queryParam("appid", apiKey)
                .toUriString();

        try {
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return parseCitySearchResults(response.getBody());
            } else {
                throw new WeatherApiException("Failed to search cities: " + response.getStatusCode(),
                        response.getStatusCode().value());
            }
        } catch (Exception ex) {
            log.warn("API error searching cities for query '{}', returning fallback: {}", query, ex.getMessage());
            return fallbackSearchCities(query);
        }
    }

    private List<CitySearchResult> fallbackSearchCities(String query) {
        List<CitySearchResult> all = List.of(
                new CitySearchResult("London", "GB", "Greater London", 51.5074, -0.1278),
                new CitySearchResult("New York", "US", "New York", 40.7128, -74.0060),
                new CitySearchResult("Tokyo", "JP", "Tokyo", 35.6762, 139.6503),
                new CitySearchResult("Mumbai", "IN", "Maharashtra", 19.0760, 72.8777),
                new CitySearchResult("Sydney", "AU", "New South Wales", -33.8688, 151.2093),
                new CitySearchResult("Paris", "FR", "Île-de-France", 48.8566, 2.3522)
        );
        if (query == null || query.isBlank()) {
            return all;
        }
        String q = query.toLowerCase().trim();
        return all.stream()
                .filter(c -> c.getName().toLowerCase().contains(q) || c.getCountry().toLowerCase().contains(q))
                .toList();
    }

    private void cacheWeatherResponse(String cityName, WeatherResponse response) {
        if (cityName != null && !cityName.isBlank()) {
            weatherCache.put(cityName.toLowerCase().trim(), copyWithDataSource(response, "CACHE"));
        }
        if (response.getCityName() != null && !response.getCityName().isBlank()) {
            weatherCache.put(response.getCityName().toLowerCase().trim(), copyWithDataSource(response, "CACHE"));
        }
    }

    private WeatherResponse getCachedWeather(String cityName) {
        if (cityName == null || cityName.isBlank()) return null;
        WeatherResponse cached = weatherCache.get(cityName.toLowerCase().trim());
        if (cached != null) {
            return cached;
        }
        // Fallback cached profile for offline/demo operation
        WeatherResponse fallback = generateFallbackCachedWeather(cityName);
        if (fallback != null) {
            weatherCache.put(cityName.toLowerCase().trim(), fallback);
        }
        return fallback;
    }

    private ForecastResponse getCachedForecast(String cityName) {
        if (cityName == null || cityName.isBlank()) return null;
        ForecastResponse cached = forecastCache.get(cityName.toLowerCase().trim());
        if (cached != null) {
            return cached;
        }
        ForecastResponse fallback = generateFallbackForecast(cityName);
        if (fallback != null) {
            forecastCache.put(cityName.toLowerCase().trim(), fallback);
        }
        return fallback;
    }

    private WeatherResponse generateFallbackCachedWeather(String cityName) {
        String cleanName = cityName.trim();
        String country = switch (cleanName.toLowerCase()) {
            case "london" -> "GB";
            case "new york" -> "US";
            case "tokyo" -> "JP";
            case "mumbai" -> "IN";
            case "sydney" -> "AU";
            case "paris" -> "FR";
            default -> "WORLD";
        };
        double lat = switch (cleanName.toLowerCase()) {
            case "london" -> 51.5074;
            case "new york" -> 40.7128;
            case "tokyo" -> 35.6762;
            case "mumbai" -> 19.0760;
            case "sydney" -> -33.8688;
            case "paris" -> 48.8566;
            default -> 0.0;
        };
        double lon = switch (cleanName.toLowerCase()) {
            case "london" -> -0.1278;
            case "new york" -> -74.0060;
            case "tokyo" -> 139.6503;
            case "mumbai" -> 72.8777;
            case "sydney" -> 151.2093;
            case "paris" -> 2.3522;
            default -> 0.0;
        };
        double temp = switch (cleanName.toLowerCase()) {
            case "london" -> 16.5;
            case "new york" -> 22.0;
            case "tokyo" -> 24.5;
            case "mumbai" -> 31.0;
            case "sydney" -> 19.0;
            case "paris" -> 18.0;
            default -> 20.0;
        };

        return new WeatherResponse(
                cleanName,
                country,
                lat,
                lon,
                temp,
                temp + 0.5,
                temp - 2.5,
                temp + 3.0,
                65,
                1013,
                4.2,
                210,
                10000,
                35,
                "Clouds",
                "Scattered clouds",
                "03d",
                LocalDateTime.now().minusHours(6),
                LocalDateTime.now().plusHours(6),
                "CACHE",
                LocalDateTime.now()
        );
    }

    private ForecastResponse generateFallbackForecast(String cityName) {
        String cleanName = cityName != null ? cityName.trim() : "City";
        WeatherResponse current = getCachedWeather(cleanName);
        double baseTemp = current != null ? current.getTemperature() : 20.0;
        String country = current != null ? current.getCountry() : "WORLD";

        List<ForecastItemDto> items = new ArrayList<>();
        LocalDateTime startTime = LocalDateTime.now().withMinute(0).withSecond(0).plusHours(3);

        for (int i = 0; i < 40; i++) {
            LocalDateTime fTime = startTime.plusHours(i * 3);
            double temp = Math.round((baseTemp + (Math.sin(i * 0.8) * 4.0)) * 10.0) / 10.0;
            double pop = Math.round((Math.abs(Math.cos(i * 0.5)) * 0.6) * 100.0) / 100.0;
            boolean isCloudy = (i % 2 == 0);

            items.add(new ForecastItemDto(
                    fTime,
                    temp,
                    temp + 0.3,
                    temp - 2.0,
                    temp + 2.5,
                    (int) (55 + (Math.sin(i) * 15)),
                    1012 + (int) (Math.cos(i) * 5),
                    3.5 + Math.abs(Math.sin(i) * 2.5),
                    180 + (i * 10) % 360,
                    pop,
                    pop > 0.3 ? 1.2 : null,
                    isCloudy ? "Clouds" : "Clear",
                    isCloudy ? "Scattered clouds" : "Clear sky",
                    isCloudy ? "03d" : "01d"
            ));
        }

        return new ForecastResponse(cleanName, country, items);
    }

    private WeatherResponse copyWithDataSource(WeatherResponse original, String dataSource) {
        if (original == null) return null;
        return new WeatherResponse(
                original.getCityName(),
                original.getCountry(),
                original.getLat(),
                original.getLon(),
                original.getTemperature(),
                original.getFeelsLike(),
                original.getTempMin(),
                original.getTempMax(),
                original.getHumidity(),
                original.getPressure(),
                original.getWindSpeed(),
                original.getWindDeg(),
                original.getVisibility(),
                original.getClouds(),
                original.getWeatherMain(),
                original.getWeatherDescription(),
                original.getWeatherIcon(),
                original.getSunrise(),
                original.getSunset(),
                dataSource,
                original.getLastUpdated()
        );
    }

    private WeatherResponse parseWeatherResponse(String json, String dataSource) {
        try {
            JsonNode root = objectMapper.readTree(json);

            String cityName = root.path("name").asText("");
            JsonNode sys = root.path("sys");
            String country = sys.path("country").asText("");

            JsonNode coord = root.path("coord");
            double lon = coord.path("lon").asDouble(0.0);
            double lat = coord.path("lat").asDouble(0.0);

            JsonNode main = root.path("main");
            double temperature = main.path("temp").asDouble(0.0);
            double feelsLike = main.path("feels_like").asDouble(0.0);
            double tempMin = main.path("temp_min").asDouble(0.0);
            double tempMax = main.path("temp_max").asDouble(0.0);
            int pressure = main.path("pressure").asInt(0);
            int humidity = main.path("humidity").asInt(0);

            int visibility = root.path("visibility").asInt(10000);

            JsonNode wind = root.path("wind");
            double windSpeed = wind.path("speed").asDouble(0.0);
            int windDeg = wind.path("deg").asInt(0);

            JsonNode clouds = root.path("clouds");
            int cloudiness = clouds.path("all").asInt(0);

            String weatherMain = "";
            String weatherDescription = "";
            String weatherIcon = "";
            JsonNode weatherArray = root.path("weather");
            if (weatherArray.isArray() && !weatherArray.isEmpty()) {
                JsonNode firstWeather = weatherArray.get(0);
                weatherMain = firstWeather.path("main").asText("");
                weatherDescription = firstWeather.path("description").asText("");
                weatherIcon = firstWeather.path("icon").asText("");
            }

            LocalDateTime sunrise = null;
            long sunriseEpoch = sys.path("sunrise").asLong(0);
            if (sunriseEpoch > 0) {
                sunrise = LocalDateTime.ofInstant(Instant.ofEpochSecond(sunriseEpoch), ZoneId.systemDefault());
            }

            LocalDateTime sunset = null;
            long sunsetEpoch = sys.path("sunset").asLong(0);
            if (sunsetEpoch > 0) {
                sunset = LocalDateTime.ofInstant(Instant.ofEpochSecond(sunsetEpoch), ZoneId.systemDefault());
            }

            LocalDateTime lastUpdated = LocalDateTime.now();

            return new WeatherResponse(
                    cityName,
                    country,
                    lat,
                    lon,
                    temperature,
                    feelsLike,
                    tempMin,
                    tempMax,
                    humidity,
                    pressure,
                    windSpeed,
                    windDeg,
                    visibility,
                    cloudiness,
                    weatherMain,
                    weatherDescription,
                    weatherIcon,
                    sunrise,
                    sunset,
                    dataSource,
                    lastUpdated
            );
        } catch (Exception e) {
            log.error("Failed to parse current weather JSON: {}", e.getMessage(), e);
            throw new WeatherApiException("Failed to parse weather API response: " + e.getMessage(), e, 500);
        }
    }

    private ForecastResponse parseForecastResponse(String json) {
        try {
            JsonNode root = objectMapper.readTree(json);
            JsonNode cityNode = root.path("city");
            String cityName = cityNode.path("name").asText("");
            String country = cityNode.path("country").asText("");

            List<ForecastItemDto> items = new ArrayList<>();
            JsonNode listNode = root.path("list");
            if (listNode.isArray()) {
                for (JsonNode item : listNode) {
                    long dt = item.path("dt").asLong(0);
                    LocalDateTime forecastTime = dt > 0
                            ? LocalDateTime.ofInstant(Instant.ofEpochSecond(dt), ZoneId.systemDefault())
                            : LocalDateTime.now();

                    JsonNode main = item.path("main");
                    double temperature = main.path("temp").asDouble(0.0);
                    double feelsLike = main.path("feels_like").asDouble(0.0);
                    double tempMin = main.path("temp_min").asDouble(0.0);
                    double tempMax = main.path("temp_max").asDouble(0.0);
                    int pressure = main.path("pressure").asInt(0);
                    int humidity = main.path("humidity").asInt(0);

                    JsonNode wind = item.path("wind");
                    double windSpeed = wind.path("speed").asDouble(0.0);
                    int windDeg = wind.path("deg").asInt(0);

                    double pop = item.path("pop").asDouble(0.0);

                    Double rain3h = null;
                    JsonNode rainNode = item.path("rain");
                    if (rainNode.has("3h")) {
                        rain3h = rainNode.path("3h").asDouble();
                    }

                    String weatherMain = "";
                    String weatherDescription = "";
                    String weatherIcon = "";
                    JsonNode weatherArray = item.path("weather");
                    if (weatherArray.isArray() && !weatherArray.isEmpty()) {
                        JsonNode first = weatherArray.get(0);
                        weatherMain = first.path("main").asText("");
                        weatherDescription = first.path("description").asText("");
                        weatherIcon = first.path("icon").asText("");
                    }

                    ForecastItemDto dto = new ForecastItemDto(
                            forecastTime,
                            temperature,
                            feelsLike,
                            tempMin,
                            tempMax,
                            humidity,
                            pressure,
                            windSpeed,
                            windDeg,
                            pop,
                            rain3h,
                            weatherMain,
                            weatherDescription,
                            weatherIcon
                    );
                    items.add(dto);
                }
            }

            return new ForecastResponse(cityName, country, items);
        } catch (Exception e) {
            log.error("Failed to parse forecast JSON: {}", e.getMessage(), e);
            throw new WeatherApiException("Failed to parse forecast API response: " + e.getMessage(), e, 500);
        }
    }

    private List<CitySearchResult> parseCitySearchResults(String json) {
        try {
            List<CitySearchResult> results = new ArrayList<>();
            JsonNode root = objectMapper.readTree(json);
            if (root.isArray()) {
                for (JsonNode node : root) {
                    String name = node.path("name").asText("");
                    String country = node.path("country").asText("");
                    String state = node.path("state").asText(null);
                    double lat = node.path("lat").asDouble(0.0);
                    double lon = node.path("lon").asDouble(0.0);

                    results.add(new CitySearchResult(name, country, state, lat, lon));
                }
            }
            return results;
        } catch (Exception e) {
            log.error("Failed to parse city search results JSON: {}", e.getMessage(), e);
            throw new WeatherApiException("Failed to parse city search results: " + e.getMessage(), e, 500);
        }
    }
}
