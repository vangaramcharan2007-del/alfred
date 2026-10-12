package com.weatherintel.service;

import com.weatherintel.dto.NotificationDto;
import com.weatherintel.entity.Notification;
import com.weatherintel.entity.User;
import com.weatherintel.entity.enums.NotificationType;
import com.weatherintel.exception.ResourceNotFoundException;
import com.weatherintel.repository.NotificationRepository;
import com.weatherintel.repository.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;

@Service
public class NotificationService {

    private static final Logger log = LoggerFactory.getLogger(NotificationService.class);

    private final NotificationRepository notificationRepository;
    private final UserRepository userRepository;

    public NotificationService(NotificationRepository notificationRepository,
                               UserRepository userRepository) {
        this.notificationRepository = notificationRepository;
        this.userRepository = userRepository;
    }

    @Transactional(readOnly = true)
    public List<NotificationDto> getNotifications(Long userId) {
        log.info("Fetching notifications for userId: {}", userId);
        List<Notification> notifications = notificationRepository.findByUserIdOrderByCreatedAtDesc(userId);
        List<NotificationDto> dtos = new ArrayList<>();
        for (Notification n : notifications) {
            dtos.add(mapToDto(n));
        }
        return dtos;
    }

    @Transactional(readOnly = true)
    public long getUnreadCount(Long userId) {
        log.info("Counting unread notifications for userId: {}", userId);
        return notificationRepository.countByUserIdAndReadFalse(userId);
    }

    @Transactional
    public void markAsRead(Long notificationId) {
        log.info("Marking notification id: {} as read", notificationId);
        Notification notification = notificationRepository.findById(notificationId)
                .orElseThrow(() -> new ResourceNotFoundException("Notification", "id", notificationId));
        notification.setRead(true);
        notificationRepository.save(notification);
    }

    @Transactional
    public void markAllAsRead(Long userId) {
        log.info("Marking all notifications for userId: {} as read", userId);
        List<Notification> unreadList = notificationRepository.findByUserIdAndReadFalse(userId);
        for (Notification n : unreadList) {
            n.setRead(true);
        }
        notificationRepository.saveAll(unreadList);
    }

    @Transactional
    public NotificationDto createNotification(Long userId, String title, String message, NotificationType type) {
        log.info("Creating notification for userId: {}, title: {}", userId, title);
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User", "id", userId));

        Notification notification = new Notification(
                user,
                null,
                title,
                message,
                type != null ? type : NotificationType.INFO
        );

        Notification saved = notificationRepository.save(notification);
        return mapToDto(saved);
    }

    private NotificationDto mapToDto(Notification n) {
        return new NotificationDto(
                n.getId(),
                n.getTitle(),
                n.getMessage(),
                n.isRead(),
                n.getNotificationType(),
                n.getCreatedAt()
        );
    }
}
