package com.weatherintel.entity;

import com.weatherintel.entity.enums.AlertType;
import jakarta.persistence.*;

import java.time.LocalDateTime;
import java.util.Objects;

@Entity
@Table(name = "alert_rules", indexes = {
        @Index(name = "idx_alert_user_enabled", columnList = "user_id, enabled"),
        @Index(name = "idx_alert_city_id", columnList = "city_id"),
        @Index(name = "idx_alert_type_enabled", columnList = "alert_type, enabled")
})
public class AlertRule {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @ManyToOne(fetch = FetchType.EAGER, optional = false)
    @JoinColumn(name = "city_id", nullable = false)
    private City city;

    @Enumerated(EnumType.STRING)
    @Column(name = "alert_type", nullable = false, length = 30)
    private AlertType alertType;

    @Column(name = "threshold_value", nullable = false)
    private double thresholdValue;

    @Column(name = "condition_value", length = 50)
    private String conditionValue;

    @Column(name = "enabled", nullable = false)
    private boolean enabled = true;

    @Column(name = "last_triggered")
    private LocalDateTime lastTriggered;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    public AlertRule() {
    }

    public AlertRule(User user, City city, AlertType alertType, double thresholdValue, String conditionValue, boolean enabled) {
        this.user = user;
        this.city = city;
        this.alertType = alertType;
        this.thresholdValue = thresholdValue;
        this.conditionValue = conditionValue;
        this.enabled = enabled;
    }

    @PrePersist
    protected void onCreate() {
        if (this.createdAt == null) {
            this.createdAt = LocalDateTime.now();
        }
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public User getUser() {
        return user;
    }

    public void setUser(User user) {
        this.user = user;
    }

    public City getCity() {
        return city;
    }

    public void setCity(City city) {
        this.city = city;
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

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        AlertRule alertRule = (AlertRule) o;
        return Objects.equals(id, alertRule.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }

    @Override
    public String toString() {
        return "AlertRule{" +
                "id=" + id +
                ", userId=" + (user != null ? user.getId() : null) +
                ", cityId=" + (city != null ? city.getId() : null) +
                ", alertType=" + alertType +
                ", thresholdValue=" + thresholdValue +
                ", conditionValue='" + conditionValue + '\'' +
                ", enabled=" + enabled +
                ", lastTriggered=" + lastTriggered +
                '}';
    }
}
