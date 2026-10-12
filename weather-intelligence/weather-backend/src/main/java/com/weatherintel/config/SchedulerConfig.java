package com.weatherintel.config;

import com.weatherintel.dto.WeatherResponse;
import com.weatherintel.entity.City;
import com.weatherintel.entity.FavoriteCity;
import com.weatherintel.repository.FavoriteCityRepository;
import com.weatherintel.service.WeatherService;
import com.weatherintel.websocket.WeatherWebSocketController;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;

import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

@Configuration
@EnableScheduling
public class SchedulerConfig {

    private static final Logger log = LoggerFactory.getLogger(SchedulerConfig.class);

    private final FavoriteCityRepository favoriteCityRepository;
    private final WeatherService weatherService;
    private final WeatherWebSocketController weatherWebSocketController;

    public SchedulerConfig(FavoriteCityRepository favoriteCityRepository,
                           WeatherService weatherService,
                           WeatherWebSocketController weatherWebSocketController) {
        this.favoriteCityRepository = favoriteCityRepository;
        this.weatherService = weatherService;
        this.weatherWebSocketController = weatherWebSocketController;
    }

    @Scheduled(fixedRateString = "#{${weather.refresh.interval-minutes:5} * 60 * 1000}")
    public void refreshFavoriteCitiesWeather() {
        log.info("Starting scheduled weather refresh for favorite cities...");
        try {
            List<FavoriteCity> favorites = favoriteCityRepository.findAll();
            Set<City> cities = favorites.stream()
                    .map(FavoriteCity::getCity)
                    .filter(city -> city != null && city.getId() != null)
                    .collect(Collectors.toSet());

            log.info("Found {} unique cities in active favorites to refresh", cities.size());

            for (City city : cities) {
                try {
                    WeatherResponse weatherResponse = weatherService.getCurrentWeatherByCityId(city.getId());
                    weatherWebSocketController.broadcastWeatherUpdate(city.getId(), weatherResponse);
                } catch (Exception ex) {
                    log.error("Failed to refresh weather for city: {} (id: {})", city.getName(), city.getId(), ex);
                }
            }
            log.info("Completed scheduled weather refresh");
        } catch (Exception ex) {
            log.error("Error during scheduled weather refresh: ", ex);
        }
    }
}
