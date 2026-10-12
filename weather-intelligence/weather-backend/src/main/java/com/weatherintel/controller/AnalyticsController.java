package com.weatherintel.controller;

import com.weatherintel.dto.AnalyticsSummary;
import com.weatherintel.dto.ComparisonPeriodDto;
import com.weatherintel.entity.WeatherSnapshot;
import com.weatherintel.service.AnalyticsService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/analytics")
public class AnalyticsController {

    private final AnalyticsService analyticsService;

    public AnalyticsController(AnalyticsService analyticsService) {
        this.analyticsService = analyticsService;
    }

    @GetMapping("/history")
    public ResponseEntity<Page<WeatherSnapshot>> getHistory(
            @RequestParam("cityId") Long cityId,
            @RequestParam("startDate") @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startDate,
            @RequestParam("endDate") @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endDate,
            @RequestParam(value = "page", defaultValue = "0") int page,
            @RequestParam(value = "size", defaultValue = "20") int size) {
        Pageable pageable = PageRequest.of(page, size);
        Page<WeatherSnapshot> history = analyticsService.getHistory(cityId, startDate, endDate, pageable);
        return ResponseEntity.ok(history);
    }

    @GetMapping("/summary")
    public ResponseEntity<AnalyticsSummary> getSummary(
            @RequestParam("cityId") Long cityId,
            @RequestParam("startDate") @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startDate,
            @RequestParam("endDate") @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endDate) {
        AnalyticsSummary summary = analyticsService.getSummary(cityId, startDate, endDate);
        return ResponseEntity.ok(summary);
    }

    @GetMapping("/compare")
    public ResponseEntity<List<ComparisonPeriodDto>> comparePeriods(
            @RequestParam("cityId") Long cityId,
            @RequestParam("p1Start") @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime p1Start,
            @RequestParam("p1End") @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime p1End,
            @RequestParam("p2Start") @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime p2Start,
            @RequestParam("p2End") @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime p2End) {
        List<ComparisonPeriodDto> comparison = analyticsService.comparePeriods(cityId, p1Start, p1End, p2Start, p2End);
        return ResponseEntity.ok(comparison);
    }

    @GetMapping("/export/csv")
    public ResponseEntity<byte[]> exportCsv(
            @RequestParam("cityId") Long cityId,
            @RequestParam("startDate") @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startDate,
            @RequestParam("endDate") @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endDate) {
        byte[] csvBytes = analyticsService.exportCsv(cityId, startDate, endDate);

        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"weather_analytics_city_" + cityId + ".csv\"")
                .contentType(MediaType.parseMediaType("text/csv"))
                .body(csvBytes);
    }
}
