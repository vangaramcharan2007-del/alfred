package com.weatherintel.service;

import com.weatherintel.dto.AnalyticsSummary;
import com.weatherintel.dto.ComparisonPeriodDto;
import com.weatherintel.entity.City;
import com.weatherintel.entity.WeatherSnapshot;
import com.weatherintel.entity.enums.DataSource;
import com.weatherintel.repository.CityRepository;
import com.weatherintel.repository.WeatherSnapshotRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.nio.charset.StandardCharsets;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class AnalyticsServiceTest {

    @Mock
    private WeatherSnapshotRepository weatherSnapshotRepository;

    @Mock
    private CityRepository cityRepository;

    @InjectMocks
    private AnalyticsService analyticsService;

    private City testCity;
    private WeatherSnapshot snap1;
    private WeatherSnapshot snap2;

    @BeforeEach
    void setUp() {
        testCity = new City(1L, "Paris", "FR", 48.8566, 2.3522, null);

        snap1 = new WeatherSnapshot();
        snap1.setId(1L);
        snap1.setCity(testCity);
        snap1.setTemperature(20.0);
        snap1.setFeelsLike(19.5);
        snap1.setTempMin(15.0);
        snap1.setTempMax(22.0);
        snap1.setHumidity(50);
        snap1.setPressure(1010);
        snap1.setWindSpeed(4.0);
        snap1.setWindDeg(180);
        snap1.setVisibility(10000);
        snap1.setClouds(20);
        snap1.setWeatherMain("Clear");
        snap1.setDataSource(DataSource.API);
        snap1.setRecordedAt(LocalDateTime.of(2026, 6, 1, 10, 0));

        snap2 = new WeatherSnapshot();
        snap2.setId(2L);
        snap2.setCity(testCity);
        snap2.setTemperature(30.0);
        snap2.setFeelsLike(31.0);
        snap2.setTempMin(25.0);
        snap2.setTempMax(32.0);
        snap2.setHumidity(70);
        snap2.setPressure(1020);
        snap2.setWindSpeed(6.0);
        snap2.setWindDeg(200);
        snap2.setVisibility(8000);
        snap2.setClouds(60);
        snap2.setWeatherMain("Rain");
        snap2.setDataSource(DataSource.API);
        snap2.setRecordedAt(LocalDateTime.of(2026, 6, 2, 10, 0));
    }

    @Test
    @DisplayName("Should correctly calculate analytics summary aggregations")
    void testGetAnalyticsSummary() {
        LocalDate start = LocalDate.of(2026, 6, 1);
        LocalDate end = LocalDate.of(2026, 6, 2);

        when(cityRepository.findById(1L)).thenReturn(Optional.of(testCity));
        when(weatherSnapshotRepository.findByCityIdAndRecordedAtBetweenOrderByRecordedAtAsc(
                eq(1L), any(LocalDateTime.class), any(LocalDateTime.class)))
                .thenReturn(List.of(snap1, snap2));

        AnalyticsSummary summary = analyticsService.getAnalyticsSummary(1L, start, end);

        assertNotNull(summary);
        assertEquals("Paris", summary.getCityName());
        assertEquals(25.0, summary.getAvgTemp()); // (20 + 30) / 2
        assertEquals(15.0, summary.getMinTemp());
        assertEquals(32.0, summary.getMaxTemp());
        assertEquals(60.0, summary.getAvgHumidity()); // (50 + 70) / 2
        assertEquals(1015.0, summary.getAvgPressure()); // (1010 + 1020) / 2
        assertEquals(5.0, summary.getAvgWindSpeed()); // (4 + 6) / 2
        assertEquals(2, summary.getTotalReadings());
    }

    @Test
    @DisplayName("Should correctly compare two periods and calculate differentials")
    void testComparePeriods() {
        LocalDate p1Start = LocalDate.of(2026, 6, 1);
        LocalDate p1End = LocalDate.of(2026, 6, 1);
        LocalDate p2Start = LocalDate.of(2026, 6, 2);
        LocalDate p2End = LocalDate.of(2026, 6, 2);

        when(cityRepository.findById(1L)).thenReturn(Optional.of(testCity));
        when(weatherSnapshotRepository.findByCityIdAndRecordedAtBetweenOrderByRecordedAtAsc(
                eq(1L), any(LocalDateTime.class), any(LocalDateTime.class)))
                .thenReturn(List.of(snap1))
                .thenReturn(List.of(snap2));

        ComparisonPeriodDto comparison = analyticsService.comparePeriods(1L, p1Start, p1End, p2Start, p2End);

        assertNotNull(comparison);
        assertEquals(10.0, comparison.getTempDiff()); // 30 - 20
        assertEquals(20.0, comparison.getHumidityDiff()); // 70 - 50
        assertEquals(10.0, comparison.getPressureDiff()); // 1020 - 1010
        assertEquals(2.0, comparison.getWindSpeedDiff()); // 6 - 4
    }

    @Test
    @DisplayName("Should generate valid CSV content on export")
    void testExportToCsv() {
        LocalDate start = LocalDate.of(2026, 6, 1);
        LocalDate end = LocalDate.of(2026, 6, 2);

        when(cityRepository.findById(1L)).thenReturn(Optional.of(testCity));
        when(weatherSnapshotRepository.findByCityIdAndRecordedAtBetweenOrderByRecordedAtAsc(
                eq(1L), any(LocalDateTime.class), any(LocalDateTime.class)))
                .thenReturn(List.of(snap1, snap2));

        byte[] csvBytes = analyticsService.exportToCsv(1L, start, end);

        assertNotNull(csvBytes);
        assertTrue(csvBytes.length > 0);

        String csvString = new String(csvBytes, StandardCharsets.UTF_8);
        assertTrue(csvString.contains("ID,City,RecordedAt,Temperature"));
        assertTrue(csvString.contains("\"Paris\""));
        assertTrue(csvString.contains("\"Clear\""));
        assertTrue(csvString.contains("\"Rain\""));
    }
}
