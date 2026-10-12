package com.weatherintel.controller;

import com.weatherintel.dto.ForecastResponse;
import com.weatherintel.dto.WeatherResponse;
import com.weatherintel.service.WeatherService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/weather")
public class WeatherController {

    private final WeatherService weatherService;

    public WeatherController(WeatherService weatherService) {
        this.weatherService = weatherService;
    }

    @GetMapping("/current")
    public ResponseEntity<WeatherResponse> getCurrentWeather(@RequestParam("city") String city) {
        WeatherResponse response = weatherService.getCurrentWeather(city);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/current/{cityId}")
    public ResponseEntity<WeatherResponse> getCurrentWeatherByCityId(@PathVariable("cityId") Long cityId) {
        WeatherResponse response = weatherService.getCurrentWeatherByCityId(cityId);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/forecast")
    public ResponseEntity<ForecastResponse> getForecast(@RequestParam("city") String city) {
        ForecastResponse response = weatherService.getForecast(city);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/multi")
    public ResponseEntity<List<WeatherResponse>> getMultiWeather(@RequestParam("cityIds") List<Long> cityIds) {
        List<WeatherResponse> responses = weatherService.getMultiWeather(cityIds);
        return ResponseEntity.ok(responses);
    }
}
