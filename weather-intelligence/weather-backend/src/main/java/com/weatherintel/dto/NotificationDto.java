package com.weatherintel.dto;

import com.weatherintel.entity.enums.NotificationType;

import java.time.LocalDateTime;

public class NotificationDto {
    private Long id;
    private Long userId;
    private Long alertRuleId;
    private String title;
    private String message;
    private boolean read;
    private NotificationType notificationType;
    private LocalDateTime createdAt;

    public NotificationDto() {
    }

    public NotificationDto(Long id, String title, String message, boolean read,
                           NotificationType notificationType, LocalDateTime createdAt) {
        this.id = id;
        this.title = title;
        this.message = message;
        this.read = read;
        this.notificationType = notificationType;
        this.createdAt = createdAt;
    }

    public NotificationDto(Long id, Long userId, Long alertRuleId, String title,
                           String message, boolean read, NotificationType notificationType, LocalDateTime createdAt) {
        this.id = id;
        this.userId = userId;
        this.alertRuleId = alertRuleId;
        this.title = title;
        this.message = message;
        this.read = read;
        this.notificationType = notificationType;
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

    public Long getAlertRuleId() {
        return alertRuleId;
    }

    public void setAlertRuleId(Long alertRuleId) {
        this.alertRuleId = alertRuleId;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public boolean isRead() {
        return read;
    }

    public void setRead(boolean read) {
        this.read = read;
    }

    public NotificationType getNotificationType() {
        return notificationType;
    }

    public void setNotificationType(NotificationType notificationType) {
        this.notificationType = notificationType;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}
