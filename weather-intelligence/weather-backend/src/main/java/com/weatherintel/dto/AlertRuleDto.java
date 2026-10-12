package com.weatherintel.dto;

import com.weatherintel.entity.enums.AlertType;
import jakarta.validation.constraints.NotNull;

import java.time.LocalDateTime;

public class AlertRuleDto {
    private Long id;
    private Long userId;

    @NotNull(message = "City ID is required")
    private Long cityId;

    private String cityName;

    @NotNull(message = "Alert type is required")
    private AlertType alertType;

    private double thresholdValue;
    private String conditionValue;
    private boolean enabled = true;
    private LocalDateTime lastTriggered;
    private LocalDateTime createdAt;

    public AlertRuleDto() {
    }

    public AlertRuleDto(Long id, Long cityId, String cityName, AlertType alertType,
                        double thresholdValue, String conditionValue, boolean enabled) {
        this.id = id;
        this.cityId = cityId;
        this.cityName = cityName;
        this.alertType = alertType;
        this.thresholdValue = thresholdValue;
        this.conditionValue = conditionValue;
        this.enabled = enabled;
    }

    public AlertRuleDto(Long id, Long userId, Long cityId, String cityName, AlertType alertType,
                        double thresholdValue, String conditionValue, boolean enabled,
                        LocalDateTime lastTriggered, LocalDateTime createdAt) {
        this.id = id;
        this.userId = userId;
        this.cityId = cityId;
        this.cityName = cityName;
        this.alertType = alertType;
        this.thresholdValue = thresholdValue;
        this.conditionValue = conditionValue;
        this.enabled = enabled;
        this.lastTriggered = lastTriggered;
        this.createdAt = createdAt;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public Long getCityId() {
        return cityId;
    }

    public void setCityId(Long cityId) {
        this.cityId = cityId;
    }

    public String getCityName() {
        return cityName;
    }

    public void setCityName(String cityName) {
        this.cityName = cityName;
    }

    public AlertType getAlertType() {
        return alertType;
    }

    public void setAlertType(AlertType alertType) {
        this.alertType = alertType;
    }

    public double getThresholdValue() {
        return thresholdValue;
    }

    public void setThresholdValue(double thresholdValue) {
        this.thresholdValue = thresholdValue;
    }

    public String getConditionValue() {
        return conditionValue;
    }

    public void setConditionValue(String conditionValue) {
        this.conditionValue = conditionValue;
    }

    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public LocalDateTime getLastTriggered() {
        return lastTriggered;
    }

    public void setLastTriggered(LocalDateTime lastTriggered) {
        this.lastTriggered = lastTriggered;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}
