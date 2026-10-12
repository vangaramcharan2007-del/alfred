package com.weatherintel.service;

import com.weatherintel.dto.AlertRuleDto;
import com.weatherintel.dto.WeatherResponse;
import com.weatherintel.entity.AlertRule;
import com.weatherintel.entity.City;
import com.weatherintel.entity.User;
import com.weatherintel.entity.enums.NotificationType;
import com.weatherintel.exception.ResourceNotFoundException;
import com.weatherintel.repository.AlertRuleRepository;
import com.weatherintel.repository.CityRepository;
import com.weatherintel.repository.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Service
public class AlertService {

    private static final Logger log = LoggerFactory.getLogger(AlertService.class);

    private final AlertRuleRepository alertRuleRepository;
    private final UserRepository userRepository;
    private final CityRepository cityRepository;
    private final NotificationService notificationService;

    public AlertService(AlertRuleRepository alertRuleRepository,
                        UserRepository userRepository,
                        CityRepository cityRepository,
                        NotificationService notificationService) {
        this.alertRuleRepository = alertRuleRepository;
        this.userRepository = userRepository;
        this.cityRepository = cityRepository;
        this.notificationService = notificationService;
    }

    @Transactional
    public AlertRuleDto createAlert(Long userId, AlertRuleDto dto) {
        log.info("Creating alert rule for userId: {} on cityId: {}", userId, dto.getCityId());
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User", "id", userId));
        City city = cityRepository.findById(dto.getCityId())
                .orElseThrow(() -> new ResourceNotFoundException("City", "id", dto.getCityId()));

        AlertRule alertRule = new AlertRule(
                user,
                city,
                dto.getAlertType(),
                dto.getThresholdValue(),
                dto.getConditionValue(),
                dto.isEnabled()
        );

        AlertRule saved = alertRuleRepository.save(alertRule);
        return mapToDto(saved);
    }

    @Transactional(readOnly = true)
    public List<AlertRuleDto> getUserAlerts(Long userId) {
        log.info("Fetching alerts for userId: {}", userId);
        List<AlertRule> rules = alertRuleRepository.findByUserId(userId);
        List<AlertRuleDto> dtos = new ArrayList<>();
        for (AlertRule rule : rules) {
            dtos.add(mapToDto(rule));
        }
        return dtos;
    }

    @Transactional
    public AlertRuleDto updateAlert(Long alertId, AlertRuleDto dto) {
        log.info("Updating alert rule id: {}", alertId);
        AlertRule rule = alertRuleRepository.findById(alertId)
                .orElseThrow(() -> new ResourceNotFoundException("AlertRule", "id", alertId));

        if (dto.getCityId() != null && (rule.getCity() == null || !rule.getCity().getId().equals(dto.getCityId()))) {
            City city = cityRepository.findById(dto.getCityId())
                    .orElseThrow(() -> new ResourceNotFoundException("City", "id", dto.getCityId()));
            rule.setCity(city);
        }

        if (dto.getAlertType() != null) {
            rule.setAlertType(dto.getAlertType());
        }
        rule.setThresholdValue(dto.getThresholdValue());
        rule.setConditionValue(dto.getConditionValue());
        rule.setEnabled(dto.isEnabled());

        AlertRule updated = alertRuleRepository.save(rule);
        return mapToDto(updated);
    }

    @Transactional
    public void deleteAlert(Long alertId) {
        log.info("Deleting alert rule id: {}", alertId);
        if (!alertRuleRepository.existsById(alertId)) {
            throw new ResourceNotFoundException("AlertRule", "id", alertId);
        }
        alertRuleRepository.deleteById(alertId);
    }

    @Transactional(readOnly = true)
    public List<AlertRuleDto> getAlertRules(Long userId) {
        return getUserAlerts(userId);
    }

    @Transactional
    public AlertRuleDto createAlertRule(Long userId, AlertRuleDto dto) {
        return createAlert(userId, dto);
    }

    @Transactional
    public AlertRuleDto updateAlertRule(Long alertId, AlertRuleDto dto) {
        return updateAlert(alertId, dto);
    }

    @Transactional
    public void deleteAlertRule(Long alertId) {
        deleteAlert(alertId);
    }

    @Transactional
    public void checkAlerts(WeatherResponse weather, Long cityId) {
        if (weather == null || cityId == null) {
            return;
        }

        log.info("Checking alerts for cityId: {} ({})", cityId, weather.getCityName());
        List<AlertRule> rules = alertRuleRepository.findByCityIdAndEnabled(cityId, true);

        for (AlertRule rule : rules) {
            boolean triggered = false;
            String message = null;

            switch (rule.getAlertType()) {
                case TEMP_ABOVE -> {
                    if (weather.getTemperature() > rule.getThresholdValue()) {
                        triggered = true;
                        message = String.format("Temperature in %s has reached %.1f°C, which is above threshold %.1f°C",
                                weather.getCityName(), weather.getTemperature(), rule.getThresholdValue());
                    }
                }
                case TEMP_BELOW -> {
                    if (weather.getTemperature() < rule.getThresholdValue()) {
                        triggered = true;
                        message = String.format("Temperature in %s is %.1f°C, falling below threshold %.1f°C",
                                weather.getCityName(), weather.getTemperature(), rule.getThresholdValue());
                    }
                }
                case HUMIDITY_ABOVE -> {
                    if (weather.getHumidity() > rule.getThresholdValue()) {
                        triggered = true;
                        message = String.format("Humidity in %s is %d%%, exceeding threshold %.0f%%",
                                weather.getCityName(), weather.getHumidity(), rule.getThresholdValue());
                    }
                }
                case WIND_ABOVE -> {
                    if (weather.getWindSpeed() > rule.getThresholdValue()) {
                        triggered = true;
                        message = String.format("Wind speed in %s has reached %.1f m/s, above threshold %.1f m/s",
                                weather.getCityName(), weather.getWindSpeed(), rule.getThresholdValue());
                    }
                }
                case WEATHER_CONDITION -> {
                    if (rule.getConditionValue() != null && !rule.getConditionValue().isBlank()) {
                        String currentCondition = weather.getWeatherMain() != null ? weather.getWeatherMain() : "";
                        if (currentCondition.equalsIgnoreCase(rule.getConditionValue().trim()) ||
                                (weather.getWeatherDescription() != null && weather.getWeatherDescription().toLowerCase().contains(rule.getConditionValue().toLowerCase().trim()))) {
                            triggered = true;
                            message = String.format("Weather condition alert: %s condition detected in %s",
                                    rule.getConditionValue(), weather.getCityName());
                        }
                    }
                }
            }

            if (triggered && message != null) {
                log.info("Alert triggered for rule id: {}: {}", rule.getId(), message);
                rule.setLastTriggered(LocalDateTime.now());
                alertRuleRepository.save(rule);

                if (rule.getUser() != null) {
                    notificationService.createNotification(
                            rule.getUser().getId(),
                            "Weather Alert: " + weather.getCityName(),
                            message,
                            NotificationType.ALERT
                    );
                }
            }
        }
    }

    private AlertRuleDto mapToDto(AlertRule rule) {
        return new AlertRuleDto(
                rule.getId(),
                rule.getCity() != null ? rule.getCity().getId() : null,
                rule.getCity() != null ? rule.getCity().getName() : null,
                rule.getAlertType(),
                rule.getThresholdValue(),
                rule.getConditionValue(),
                rule.isEnabled()
        );
    }
}
