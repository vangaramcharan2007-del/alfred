package com.weatherintel.config;

import com.weatherintel.entity.City;
import com.weatherintel.entity.User;
import com.weatherintel.entity.WeatherSnapshot;
import com.weatherintel.entity.enums.DataSource;
import com.weatherintel.entity.enums.Role;
import com.weatherintel.repository.CityRepository;
import com.weatherintel.repository.UserRepository;
import com.weatherintel.repository.WeatherSnapshotRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.List;

@Component
public class DataInitializer implements CommandLineRunner {

    private static final Logger log = LoggerFactory.getLogger(DataInitializer.class);

    private final UserRepository userRepository;
    private final CityRepository cityRepository;
    private final WeatherSnapshotRepository weatherSnapshotRepository;
    private final PasswordEncoder passwordEncoder;

    public DataInitializer(UserRepository userRepository,
                           CityRepository cityRepository,
                           WeatherSnapshotRepository weatherSnapshotRepository,
                           PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.cityRepository = cityRepository;
        this.weatherSnapshotRepository = weatherSnapshotRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public void run(String... args) {
        log.info("Checking database initialization...");

        // 1. Seed Users
        if (userRepository.count() == 0) {
            log.info("Seeding default users...");
            User admin = new User("admin", passwordEncoder.encode("admin123"), "admin@weatherintel.com", Role.ADMIN);
            User user = new User("user", passwordEncoder.encode("user123"), "user@weatherintel.com", Role.USER);
            userRepository.saveAll(List.of(admin, user));
            log.info("Default users seeded (admin, user)");
        }

        // 2. Seed Cities
        if (cityRepository.count() == 0) {
            log.info("Seeding default monitoring cities...");
            List<City> cities = List.of(
                    new City("London", "GB", 51.5074, -0.1278, "Greater London"),
                    new City("New York", "US", 40.7128, -74.0060, "New York"),
                    new City("Tokyo", "JP", 35.6762, 139.6503, "Tokyo"),
                    new City("Mumbai", "IN", 19.0760, 72.8777, "Maharashtra"),
                    new City("Sydney", "AU", -33.8688, 151.2093, "New South Wales"),
                    new City("Paris", "FR", 48.8566, 2.3522, "Île-de-France")
            );
            List<City> savedCities = cityRepository.saveAll(cities);
            log.info("Seeded {} monitoring cities", savedCities.size());

            // 3. Seed initial historical weather snapshots for analytics demonstration
            for (City city : savedCities) {
                for (int i = 5; i >= 0; i--) {
                    WeatherSnapshot snapshot = new WeatherSnapshot();
                    snapshot.setCity(city);
                    double baseTemp = switch (city.getName()) {
                        case "London" -> 16.5;
                        case "New York" -> 22.0;
                        case "Tokyo" -> 24.5;
                        case "Mumbai" -> 31.0;
                        case "Sydney" -> 19.0;
                        case "Paris" -> 18.0;
                        default -> 20.0;
                    };
                    double temp = Math.round((baseTemp + (Math.sin(i) * 3.5)) * 10.0) / 10.0;
                    snapshot.setTemperature(temp);
                    snapshot.setFeelsLike(Math.round((temp + 0.5) * 10.0) / 10.0);
                    snapshot.setTempMin(temp - 2.5);
                    snapshot.setTempMax(temp + 3.0);
                    snapshot.setHumidity((int) (60 + (i * 3)));
                    snapshot.setPressure(1013 - i);
                    snapshot.setWindSpeed(3.5 + (i * 0.5));
                    snapshot.setWindDeg(180 + (i * 15));
                    snapshot.setVisibility(10000);
                    snapshot.setClouds(30 + (i * 5));
                    snapshot.setWeatherMain(i % 2 == 0 ? "Clouds" : "Clear");
                    snapshot.setWeatherDescription(i % 2 == 0 ? "Scattered clouds" : "Clear sky");
                    snapshot.setWeatherIcon(i % 2 == 0 ? "03d" : "01d");
                    snapshot.setDataSource(DataSource.CACHE);
                    snapshot.setRecordedAt(LocalDateTime.now().minusHours(i * 4));
                    snapshot.setCreatedAt(LocalDateTime.now().minusHours(i * 4));
                    weatherSnapshotRepository.save(snapshot);
                }
            }
            log.info("Seeded initial historical snapshots for analytics and offline fallback.");
        }
    }
}
