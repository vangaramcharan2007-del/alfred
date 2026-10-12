package com.weatherintel.service;

import com.weatherintel.dto.CitySearchResult;
import com.weatherintel.entity.City;
import com.weatherintel.exception.ResourceNotFoundException;
import com.weatherintel.repository.CityRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
public class CityService {

    private static final Logger log = LoggerFactory.getLogger(CityService.class);

    private final CityRepository cityRepository;
    private final OpenWeatherApiClient apiClient;

    public CityService(CityRepository cityRepository, OpenWeatherApiClient apiClient) {
        this.cityRepository = cityRepository;
        this.apiClient = apiClient;
    }

    public List<CitySearchResult> searchCities(String query) {
        log.info("Searching cities with query: {}", query);
        return apiClient.searchCities(query);
    }

    @Transactional
    public City addCity(String name, String country, double lat, double lon) {
        log.info("Adding city: {} ({}) [{}, {}]", name, country, lat, lon);
        Optional<City> existing = cityRepository.findFirstByNameIgnoreCaseAndCountryIgnoreCase(name, country);
        if (existing.isPresent()) {
            City city = existing.get();
            city.setLatitude(lat);
            city.setLongitude(lon);
            return cityRepository.save(city);
        }

        City city = new City(name, country, lat, lon);
        return cityRepository.save(city);
    }

    @Transactional
    public City createCity(String name, String country, Double lat, Double lon, String state) {
        log.info("Creating city: {} ({})", name, country);
        double latitude = lat != null ? lat : 0.0;
        double longitude = lon != null ? lon : 0.0;
        City city = new City(name, country, latitude, longitude, state);
        return cityRepository.save(city);
    }

    @Transactional
    public City getOrCreateCity(String name, String country, double lat, double lon) {
        log.info("Getting or creating city: {} ({})", name, country);
        return cityRepository.findFirstByNameIgnoreCaseAndCountryIgnoreCase(name, country)
                .orElseGet(() -> {
                    City newCity = new City(name, country, lat, lon);
                    return cityRepository.save(newCity);
                });
    }

    @Transactional(readOnly = true)
    public List<City> getAllCities() {
        log.info("Fetching all cities");
        return cityRepository.findAll();
    }

    @Transactional(readOnly = true)
    public City getCityById(Long id) {
        log.info("Fetching city by id: {}", id);
        return cityRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("City", "id", id));
    }
}
