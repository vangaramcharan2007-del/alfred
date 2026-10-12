package com.weatherintel.controller;

import com.weatherintel.dto.CitySearchResult;
import com.weatherintel.dto.CreateCityRequest;
import com.weatherintel.entity.City;
import com.weatherintel.service.CityService;
import com.weatherintel.service.WeatherService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/cities")
public class CityController {

    private final CityService cityService;
    private final WeatherService weatherService;

    public CityController(CityService cityService, WeatherService weatherService) {
        this.cityService = cityService;
        this.weatherService = weatherService;
    }

    @GetMapping("/search")
    public ResponseEntity<List<CitySearchResult>> searchCities(@RequestParam("q") String query) {
        List<CitySearchResult> results = cityService.searchCities(query);
        return ResponseEntity.ok(results);
    }

    @GetMapping
    public ResponseEntity<List<City>> getAllCities() {
        List<City> cities = cityService.getAllCities();
        return ResponseEntity.ok(cities);
    }

    @GetMapping("/{id}")
    public ResponseEntity<City> getCityById(@PathVariable("id") Long id) {
        City city = cityService.getCityById(id);
        return ResponseEntity.ok(city);
    }

    @PostMapping
    public ResponseEntity<City> createCity(@Valid @RequestBody CreateCityRequest request) {
        City createdCity = cityService.createCity(
                request.getName(),
                request.getCountry(),
                request.getLat(),
                request.getLon(),
                request.getState()
        );
        return new ResponseEntity<>(createdCity, HttpStatus.CREATED);
    }
}
