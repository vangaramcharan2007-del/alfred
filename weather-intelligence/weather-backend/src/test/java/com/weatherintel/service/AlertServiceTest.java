package com.weatherintel.service;

import com.weatherintel.dto.AlertRuleDto;
import com.weatherintel.dto.WeatherResponse;
import com.weatherintel.entity.AlertRule;
import com.weatherintel.entity.City;
import com.weatherintel.entity.User;
import com.weatherintel.entity.enums.AlertType;
import com.weatherintel.entity.enums.NotificationType;
import com.weatherintel.entity.enums.Role;
import com.weatherintel.repository.AlertRuleRepository;
import com.weatherintel.repository.CityRepository;
import com.weatherintel.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AlertServiceTest {

    @Mock
    private AlertRuleRepository alertRuleRepository;

    @Mock
    private UserRepository userRepository;

    @Mock
    private CityRepository cityRepository;

    @Mock
    private NotificationService notificationService;

    @InjectMocks
    private AlertService alertService;

    private User testUser;
    private City testCity;

    @BeforeEach
    void setUp() {
        testUser = new User("testuser", "hashedpass", "test@example.com", Role.USER);
        testUser.setId(100L);

        testCity = new City(1L, "London", "GB", 51.5074, -0.1278, null);
    }

    @Test
    @DisplayName("Should create alert rule successfully")
    void testCreateAlertSuccess() {
        AlertRuleDto requestDto = new AlertRuleDto(
                null, 1L, "London", AlertType.TEMP_ABOVE, 30.0, null, true
        );

        when(userRepository.findById(100L)).thenReturn(Optional.of(testUser));
        when(cityRepository.findById(1L)).thenReturn(Optional.of(testCity));
        when(alertRuleRepository.save(any(AlertRule.class))).thenAnswer(inv -> {
            AlertRule rule = inv.getArgument(0);
            rule.setId(50L);
            return rule;
        });

        AlertRuleDto created = alertService.createAlert(100L, requestDto);

        assertNotNull(created);
        assertEquals(50L, created.getId());
        assertEquals(AlertType.TEMP_ABOVE, created.getAlertType());
        assertEquals(30.0, created.getThresholdValue());
        assertTrue(created.isEnabled());

        verify(alertRuleRepository, times(1)).save(any(AlertRule.class));
    }

    @Test
    @DisplayName("Should trigger notification when temperature exceeds threshold")
    void testCheckAlertsTriggered() {
        AlertRule rule = new AlertRule(testUser, testCity, AlertType.TEMP_ABOVE, 25.0, null, true);
        rule.setId(1L);

        when(alertRuleRepository.findByCityIdAndEnabled(1L, true)).thenReturn(List.of(rule));

        WeatherResponse weather = new WeatherResponse(
                "London", "GB", 51.5, -0.1,
                32.0, 34.0, 20.0, 33.0,
                50, 1010, 5.0, 180,
                10000, 10, "Clear", "Clear sky",
                "01d", LocalDateTime.now(), LocalDateTime.now(),
                "API", LocalDateTime.now()
        );

        alertService.checkAlerts(weather, 1L);

        verify(notificationService, times(1)).createNotification(
                eq(100L),
                contains("Weather Alert"),
                contains("above threshold"),
                eq(NotificationType.ALERT)
        );
        verify(alertRuleRepository, times(1)).save(rule);
        assertNotNull(rule.getLastTriggered());
    }

    @Test
    @DisplayName("Should not trigger notification when temperature is within threshold")
    void testCheckAlertsNotTriggered() {
        AlertRule rule = new AlertRule(testUser, testCity, AlertType.TEMP_ABOVE, 35.0, null, true);
        rule.setId(1L);

        when(alertRuleRepository.findByCityIdAndEnabled(1L, true)).thenReturn(List.of(rule));

        WeatherResponse weather = new WeatherResponse(
                "London", "GB", 51.5, -0.1,
                20.0, 19.0, 15.0, 22.0,
                60, 1012, 3.0, 180,
                10000, 20, "Clouds", "Few clouds",
                "02d", LocalDateTime.now(), LocalDateTime.now(),
                "API", LocalDateTime.now()
        );

        alertService.checkAlerts(weather, 1L);

        verify(notificationService, never()).createNotification(anyLong(), anyString(), anyString(), any());
    }
}
