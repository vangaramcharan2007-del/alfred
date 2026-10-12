package com.weatherintel.service;

import com.weatherintel.dto.ForecastItemDto;
import com.weatherintel.dto.ForecastResponse;
import com.weatherintel.dto.WeatherResponse;
import com.weatherintel.entity.City;
import com.weatherintel.entity.ForecastEntry;
import com.weatherintel.entity.WeatherSnapshot;
import com.weatherintel.entity.enums.DataSource;
import com.weatherintel.exception.ResourceNotFoundException;
import com.weatherintel.repository.CityRepository;
import com.weatherintel.repository.ForecastEntryRepository;
import com.weatherintel.repository.WeatherSnapshotRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Service
public class WeatherService {

    private static final Logger log = LoggerFactory.getLogger(WeatherService.class);

    private final OpenWeatherApiClient apiClient;
    private final WeatherSnapshotRepository weatherSnapshotRepository;
    private final ForecastEntryRepository forecastEntryRepository;
    private final CityRepository cityRepository;

    public WeatherService(OpenWeatherApiClient apiClient,
                          WeatherSnapshotRepository weatherSnapshotRepository,
                          ForecastEntryRepository forecastEntryRepository,
                          CityRepository cityRepository) {
        this.apiClient = apiClient;
        this.weatherSnapshotRepository = weatherSnapshotRepository;
        this.forecastEntryRepository = forecastEntryRepository;
        this.cityRepository = cityRepository;
    }

    @Transactional
    public WeatherResponse getWeather(String cityName) {
        log.info("Processing weather request for city: {}", cityName);
        WeatherResponse response = apiClient.getCurrentWeather(cityName);

        City city = resolveCity(response.getCityName(), response.getCountry(), response.getLat(), response.getLon());
        saveWeatherSnapshot(city, response);

        return response;
    }

    public WeatherResponse getCurrentWeather(String cityName) {
        return getWeather(cityName);
    }

    public WeatherResponse getCurrentWeatherByCityId(Long cityId) {
        return getWeatherForCity(cityId);
    }

    public List<WeatherResponse> getMultiWeather(List<Long> cityIds) {
        return getMultiCityWeather(cityIds);
    }

    public List<com.weatherintel.dto.CitySearchResult> searchCities(String query) {
        return apiClient.searchCities(query);
    }

    @Transactional
    public WeatherResponse getWeatherForCity(Long cityId) {
        log.info("Processing weather request for cityId: {}", cityId);
        City city = cityRepository.findById(cityId)
                .orElseThrow(() -> new ResourceNotFoundException("City", "id", cityId));

        WeatherResponse response;
        if (city.getLatitude() != 0.0 || city.getLongitude() != 0.0) {
            response = apiClient.getCurrentWeatherByCoords(city.getLatitude(), city.getLongitude());
        } else {
            response = apiClient.getCurrentWeather(city.getName());
        }

        saveWeatherSnapshot(city, response);
        return response;
    }

    @Transactional
    public ForecastResponse getForecast(String cityName) {
        log.info("Processing forecast request for city: {}", cityName);
        ForecastResponse forecast = apiClient.getForecast(cityName);

        Optional<City> cityOpt = cityRepository.findFirstByNameIgnoreCaseAndCountryIgnoreCase(
                forecast.getCityName(), forecast.getCountry());
        City city = cityOpt.orElseGet(() -> {
            City newCity = new City(forecast.getCityName(), forecast.getCountry(), 0.0, 0.0);
            return cityRepository.save(newCity);
        });

        // Delete old forecast entries for this city
        forecastEntryRepository.deleteByCityId(city.getId());

        List<ForecastEntry> entriesToSave = new ArrayList<>();
        if (forecast.getForecasts() != null) {
            for (ForecastItemDto item : forecast.getForecasts()) {
                ForecastEntry entry = new ForecastEntry();
                entry.setCity(city);
                entry.setForecastTime(item.getForecastTime() != null ? item.getForecastTime() : LocalDateTime.now());
                entry.setTemperature(item.getTemperature());
                entry.setFeelsLike(item.getFeelsLike());
                entry.setTempMin(item.getTempMin());
                entry.setTempMax(item.getTempMax());
                entry.setHumidity(item.getHumidity());
                entry.setPressure(item.getPressure());
                entry.setWindSpeed(item.getWindSpeed());
                entry.setWindDeg(item.getWindDeg());
                entry.setPop(item.getPop());
                entry.setRain3h(item.getRain3h());
                entry.setWeatherMain(item.getWeatherMain());
                entry.setWeatherDescription(item.getWeatherDescription());
                entry.setWeatherIcon(item.getWeatherIcon());
                entry.setCreatedAt(LocalDateTime.now());
                entriesToSave.add(entry);
            }
            forecastEntryRepository.saveAll(entriesToSave);
            log.info("Saved {} forecast entries for city: {}", entriesToSave.size(), city.getName());
        }

        return forecast;
    }

    @Transactional
    public List<WeatherResponse> getMultiCityWeather(List<Long> cityIds) {
        log.info("Processing multi-city weather request for {} cities", cityIds != null ? cityIds.size() : 0);
        List<WeatherResponse> results = new ArrayList<>();
        if (cityIds == null || cityIds.isEmpty()) {
            return results;
        }

        for (Long cityId : cityIds) {
            try {
                WeatherResponse weather = getWeatherForCity(cityId);
                results.add(weather);
            } catch (Exception ex) {
                log.error("Failed to fetch weather for cityId {}: {}", cityId, ex.getMessage());
                // Fall back to most recent snapshot in database if present
                Optional<WeatherSnapshot> latestSnapshot = weatherSnapshotRepository.findTopByCityIdOrderByRecordedAtDesc(cityId);
                latestSnapshot.ifPresent(snapshot -> results.add(convertToResponse(snapshot, "CACHE")));
            }
        }
        return results;
    }

    private City resolveCity(String name, String country, double lat, double lon) {
        Optional<City> existing = cityRepository.findFirstByNameIgnoreCaseAndCountryIgnoreCase(name, country);
        if (existing.isPresent()) {
            City city = existing.get();
            if (city.getLatitude() == 0.0 && city.getLongitude() == 0.0 && (lat != 0.0 || lon != 0.0)) {
                city.setLatitude(lat);
                city.setLongitude(lon);
                city = cityRepository.save(city);
            }
            return city;
        }

        City newCity = new City(name, country, lat, lon);
        return cityRepository.save(newCity);
    }

    private WeatherSnapshot saveWeatherSnapshot(City city, WeatherResponse response) {
        WeatherSnapshot snapshot = new WeatherSnapshot();
        snapshot.setCity(city);
        snapshot.setTemperature(response.getTemperature());
        snapshot.setFeelsLike(response.getFeelsLike());
        snapshot.setTempMin(response.getTempMin());
        snapshot.setTempMax(response.getTempMax());
        snapshot.setHumidity(response.getHumidity());
        snapshot.setPressure(response.getPressure());
        snapshot.setWindSpeed(response.getWindSpeed());
        snapshot.setWindDeg(response.getWindDeg());
        snapshot.setVisibility(response.getVisibility());
        snapshot.setClouds(response.getClouds());
        snapshot.setWeatherMain(response.getWeatherMain());
        snapshot.setWeatherDescription(response.getWeatherDescription());
        snapshot.setWeatherIcon(response.getWeatherIcon());
        snapshot.setSunrise(response.getSunrise());
        snapshot.setSunset(response.getSunset());
        snapshot.setDataSource("CACHE".equalsIgnoreCase(response.getDataSource()) ? DataSource.CACHE : DataSource.API);
        snapshot.setRecordedAt(response.getLastUpdated() != null ? response.getLastUpdated() : LocalDateTime.now());
        snapshot.setCreatedAt(LocalDateTime.now());

        WeatherSnapshot saved = weatherSnapshotRepository.save(snapshot);
        log.info("Saved weather snapshot id={} for city={}", saved.getId(), city.getName());
        return saved;
    }

    private WeatherResponse convertToResponse(WeatherSnapshot snapshot, String dataSource) {
        City city = snapshot.getCity();
        return new WeatherResponse(
                city != null ? city.getName() : "Unknown",
                city != null ? city.getCountry() : "",
                city != null ? city.getLatitude() : 0.0,
                city != null ? city.getLongitude() : 0.0,
                snapshot.getTemperature(),
                snapshot.getFeelsLike(),
                snapshot.getTempMin(),
                snapshot.getTempMax(),
                snapshot.getHumidity(),
                snapshot.getPressure(),
                snapshot.getWindSpeed(),
                snapshot.getWindDeg(),
                snapshot.getVisibility(),
                snapshot.getClouds(),
                snapshot.getWeatherMain(),
                snapshot.getWeatherDescription(),
                snapshot.getWeatherIcon(),
                snapshot.getSunrise(),
                snapshot.getSunset(),
                dataSource,
                snapshot.getRecordedAt()
        );
    }
}
