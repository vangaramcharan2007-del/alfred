package com.weatherintel.service;

import com.weatherintel.dto.AnalyticsSummary;
import com.weatherintel.dto.ComparisonPeriodDto;
import com.weatherintel.entity.City;
import com.weatherintel.entity.WeatherSnapshot;
import com.weatherintel.exception.ResourceNotFoundException;
import com.weatherintel.repository.CityRepository;
import com.weatherintel.repository.WeatherSnapshotRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.ByteArrayOutputStream;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.List;

@Service
public class AnalyticsService {

    private static final Logger log = LoggerFactory.getLogger(AnalyticsService.class);

    private final WeatherSnapshotRepository weatherSnapshotRepository;
    private final CityRepository cityRepository;

    public AnalyticsService(WeatherSnapshotRepository weatherSnapshotRepository,
                            CityRepository cityRepository) {
        this.weatherSnapshotRepository = weatherSnapshotRepository;
        this.cityRepository = cityRepository;
    }

    @Transactional(readOnly = true)
    public Page<WeatherSnapshot> getHistoricalData(Long cityId, LocalDate startDate, LocalDate endDate, Pageable pageable) {
        log.info("Fetching historical data for cityId: {} from {} to {}", cityId, startDate, endDate);
        LocalDateTime start = startDate.atStartOfDay();
        LocalDateTime end = endDate.atTime(LocalTime.MAX);
        return weatherSnapshotRepository.findByCityIdAndRecordedAtBetween(cityId, start, end, pageable);
    }

    @Transactional(readOnly = true)
    public AnalyticsSummary getAnalyticsSummary(Long cityId, LocalDate startDate, LocalDate endDate) {
        log.info("Calculating analytics summary for cityId: {} between {} and {}", cityId, startDate, endDate);
        City city = cityRepository.findById(cityId)
                .orElseThrow(() -> new ResourceNotFoundException("City", "id", cityId));

        LocalDateTime start = startDate.atStartOfDay();
        LocalDateTime end = endDate.atTime(LocalTime.MAX);
        List<WeatherSnapshot> snapshots = weatherSnapshotRepository.findByCityIdAndRecordedAtBetweenOrderByRecordedAtAsc(cityId, start, end);

        if (snapshots.isEmpty()) {
            return new AnalyticsSummary(city.getName(), startDate, endDate, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0);
        }

        double sumTemp = 0.0;
        double minTemp = Double.MAX_VALUE;
        double maxTemp = -Double.MAX_VALUE;
        double sumHumidity = 0.0;
        double sumPressure = 0.0;
        double sumWindSpeed = 0.0;

        for (WeatherSnapshot s : snapshots) {
            sumTemp += s.getTemperature();
            minTemp = Math.min(minTemp, s.getTempMin());
            maxTemp = Math.max(maxTemp, s.getTempMax());
            sumHumidity += s.getHumidity();
            sumPressure += s.getPressure();
            sumWindSpeed += s.getWindSpeed();
        }

        int count = snapshots.size();
        double avgTemp = Math.round((sumTemp / count) * 100.0) / 100.0;
        double avgHumidity = Math.round((sumHumidity / count) * 100.0) / 100.0;
        double avgPressure = Math.round((sumPressure / count) * 100.0) / 100.0;
        double avgWindSpeed = Math.round((sumWindSpeed / count) * 100.0) / 100.0;

        return new AnalyticsSummary(
                city.getName(),
                startDate,
                endDate,
                avgTemp,
                minTemp,
                maxTemp,
                avgHumidity,
                avgPressure,
                avgWindSpeed,
                count
        );
    }

    @Transactional(readOnly = true)
    public ComparisonPeriodDto comparePeriods(Long cityId, LocalDate period1Start, LocalDate period1End,
                                              LocalDate period2Start, LocalDate period2End) {
        log.info("Comparing periods for cityId: {} [{} - {}] vs [{} - {}]", cityId, period1Start, period1End, period2Start, period2End);
        AnalyticsSummary period1 = getAnalyticsSummary(cityId, period1Start, period1End);
        AnalyticsSummary period2 = getAnalyticsSummary(cityId, period2Start, period2End);

        double tempDiff = Math.round((period2.getAvgTemp() - period1.getAvgTemp()) * 100.0) / 100.0;
        double humidityDiff = Math.round((period2.getAvgHumidity() - period1.getAvgHumidity()) * 100.0) / 100.0;
        double pressureDiff = Math.round((period2.getAvgPressure() - period1.getAvgPressure()) * 100.0) / 100.0;
        double windSpeedDiff = Math.round((period2.getAvgWindSpeed() - period1.getAvgWindSpeed()) * 100.0) / 100.0;

        return new ComparisonPeriodDto(period1, period2, tempDiff, humidityDiff, pressureDiff, windSpeedDiff);
    }

    @Transactional(readOnly = true)
    public byte[] exportToCsv(Long cityId, LocalDate startDate, LocalDate endDate) {
        log.info("Exporting CSV for cityId: {} from {} to {}", cityId, startDate, endDate);
        City city = cityRepository.findById(cityId)
                .orElseThrow(() -> new ResourceNotFoundException("City", "id", cityId));

        LocalDateTime start = startDate.atStartOfDay();
        LocalDateTime end = endDate.atTime(LocalTime.MAX);
        List<WeatherSnapshot> snapshots = weatherSnapshotRepository.findByCityIdAndRecordedAtBetweenOrderByRecordedAtAsc(cityId, start, end);

        ByteArrayOutputStream out = new ByteArrayOutputStream();
        try (PrintWriter writer = new PrintWriter(out, true, StandardCharsets.UTF_8)) {
            writer.println("ID,City,RecordedAt,Temperature,FeelsLike,TempMin,TempMax,Humidity,Pressure,WindSpeed,WindDeg,Visibility,Clouds,Condition,DataSource");
            for (WeatherSnapshot s : snapshots) {
                writer.printf("%d,\"%s\",\"%s\",%.2f,%.2f,%.2f,%.2f,%d,%d,%.2f,%d,%d,%d,\"%s\",\"%s\"%n",
                        s.getId(),
                        city.getName(),
                        s.getRecordedAt(),
                        s.getTemperature(),
                        s.getFeelsLike(),
                        s.getTempMin(),
                        s.getTempMax(),
                        s.getHumidity(),
                        s.getPressure(),
                        s.getWindSpeed(),
                        s.getWindDeg(),
                        s.getVisibility(),
                        s.getClouds(),
                        s.getWeatherMain() != null ? s.getWeatherMain() : "",
                        s.getDataSource() != null ? s.getDataSource().name() : ""
                );
            }
            writer.flush();
        }
        return out.toByteArray();
    }

    @Transactional(readOnly = true)
    public Page<WeatherSnapshot> getHistory(Long cityId, LocalDateTime startDate, LocalDateTime endDate, Pageable pageable) {
        return weatherSnapshotRepository.findByCityIdAndRecordedAtBetween(cityId, startDate, endDate, pageable);
    }

    @Transactional(readOnly = true)
    public AnalyticsSummary getSummary(Long cityId, LocalDateTime startDate, LocalDateTime endDate) {
        return getAnalyticsSummary(cityId, startDate.toLocalDate(), endDate.toLocalDate());
    }

    @Transactional(readOnly = true)
    public List<ComparisonPeriodDto> comparePeriods(Long cityId, LocalDateTime p1Start, LocalDateTime p1End,
                                                    LocalDateTime p2Start, LocalDateTime p2End) {
        ComparisonPeriodDto dto = comparePeriods(cityId, p1Start.toLocalDate(), p1End.toLocalDate(),
                                                 p2Start.toLocalDate(), p2End.toLocalDate());
        return List.of(dto);
    }

    @Transactional(readOnly = true)
    public byte[] exportCsv(Long cityId, LocalDateTime startDate, LocalDateTime endDate) {
        return exportToCsv(cityId, startDate.toLocalDate(), endDate.toLocalDate());
    }
}
