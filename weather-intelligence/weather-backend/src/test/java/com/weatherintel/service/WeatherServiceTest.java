package com.weatherintel.service;

import com.weatherintel.dto.ForecastItemDto;
import com.weatherintel.dto.ForecastResponse;
import com.weatherintel.dto.WeatherResponse;
import com.weatherintel.entity.City;
import com.weatherintel.entity.WeatherSnapshot;
import com.weatherintel.entity.enums.DataSource;
import com.weatherintel.exception.WeatherApiException;
import com.weatherintel.repository.CityRepository;
import com.weatherintel.repository.ForecastEntryRepository;
import com.weatherintel.repository.WeatherSnapshotRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class WeatherServiceTest {

    @Mock
    private OpenWeatherApiClient apiClient;

    @Mock
    private WeatherSnapshotRepository weatherSnapshotRepository;

    @Mock
    private ForecastEntryRepository forecastEntryRepository;

    @Mock
    private CityRepository cityRepository;

    @InjectMocks
    private WeatherService weatherService;

    private City testCity;
    private WeatherResponse sampleWeather;

    @BeforeEach
    void setUp() {
        testCity = new City(1L, "London", "GB", 51.5074, -0.1278, null);
        testCity.setCreatedAt(LocalDateTime.now());

        sampleWeather = new WeatherResponse(
                "London", "GB", 51.5074, -0.1278,
                18.5, 17.8, 15.0, 21.0,
                65, 1012, 4.5, 230,
                10000, 40, "Clouds", "Scattered clouds",
                "03d", LocalDateTime.now().minusHours(6), LocalDateTime.now().plusHours(6),
                "API", LocalDateTime.now()
        );
    }

    @Test
    @DisplayName("Should fetch weather and persist snapshot successfully")
    void testGetWeatherSuccess() {
        when(apiClient.getCurrentWeather("London")).thenReturn(sampleWeather);
        when(cityRepository.findFirstByNameIgnoreCaseAndCountryIgnoreCase("London", "GB"))
                .thenReturn(Optional.of(testCity));
        when(weatherSnapshotRepository.save(any(WeatherSnapshot.class))).thenAnswer(invocation -> invocation.getArgument(0));

        WeatherResponse result = weatherService.getWeather("London");

        assertNotNull(result);
        assertEquals("London", result.getCityName());
        assertEquals(18.5, result.getTemperature());
        assertEquals("API", result.getDataSource());

        verify(apiClient, times(1)).getCurrentWeather("London");
        verify(weatherSnapshotRepository, times(1)).save(any(WeatherSnapshot.class));
    }

    @Test
    @DisplayName("Should fetch forecast and persist forecast entries")
    void testGetForecastSuccess() {
        ForecastItemDto item = new ForecastItemDto(
                LocalDateTime.now().plusHours(3),
                19.0, 18.2, 16.0, 20.0,
                60, 1013, 3.8, 220, 0.1, null,
                "Clear", "Clear sky", "01d"
        );
        ForecastResponse forecastResponse = new ForecastResponse("London", "GB", List.of(item));

        when(apiClient.getForecast("London")).thenReturn(forecastResponse);
        when(cityRepository.findFirstByNameIgnoreCaseAndCountryIgnoreCase("London", "GB"))
                .thenReturn(Optional.of(testCity));

        ForecastResponse result = weatherService.getForecast("London");

        assertNotNull(result);
        assertEquals("London", result.getCityName());
        assertEquals(1, result.getForecasts().size());

        verify(forecastEntryRepository, times(1)).deleteByCityId(1L);
        verify(forecastEntryRepository, times(1)).saveAll(anyList());
    }

    @Test
    @DisplayName("Should retrieve multi-city weather and fallback to cached snapshot on API failure")
    void testGetMultiCityWeatherWithFallback() {
        when(cityRepository.findById(1L)).thenReturn(Optional.of(testCity));
        when(apiClient.getCurrentWeatherByCoords(51.5074, -0.1278)).thenThrow(new WeatherApiException("API unreachable", 502));

        WeatherSnapshot cachedSnapshot = new WeatherSnapshot();
        cachedSnapshot.setId(10L);
        cachedSnapshot.setCity(testCity);
        cachedSnapshot.setTemperature(16.0);
        cachedSnapshot.setFeelsLike(15.5);
        cachedSnapshot.setTempMin(14.0);
        cachedSnapshot.setTempMax(18.0);
        cachedSnapshot.setHumidity(70);
        cachedSnapshot.setPressure(1015);
        cachedSnapshot.setWindSpeed(3.0);
        cachedSnapshot.setWindDeg(180);
        cachedSnapshot.setVisibility(9000);
        cachedSnapshot.setClouds(50);
        cachedSnapshot.setWeatherMain("Clouds");
        cachedSnapshot.setWeatherDescription("Broken clouds");
        cachedSnapshot.setWeatherIcon("04d");
        cachedSnapshot.setDataSource(DataSource.CACHE);
        cachedSnapshot.setRecordedAt(LocalDateTime.now().minusHours(1));

        when(weatherSnapshotRepository.findTopByCityIdOrderByRecordedAtDesc(1L))
                .thenReturn(Optional.of(cachedSnapshot));

        List<WeatherResponse> results = weatherService.getMultiCityWeather(List.of(1L));

        assertNotNull(results);
        assertEquals(1, results.size());
        assertEquals("CACHE", results.getFirst().getDataSource());
        assertEquals(16.0, results.getFirst().getTemperature());
    }
}
