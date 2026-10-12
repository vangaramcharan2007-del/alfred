package com.weatherintel.service;

import com.weatherintel.entity.AuditRecord;
import com.weatherintel.repository.AuditRecordRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class AuditService {

    private static final Logger log = LoggerFactory.getLogger(AuditService.class);

    private final AuditRecordRepository auditRecordRepository;

    public AuditService(AuditRecordRepository auditRecordRepository) {
        this.auditRecordRepository = auditRecordRepository;
    }

    @Transactional
    public void log(String username, String action, String details, String ipAddress) {
        log.info("Audit log: user='{}', action='{}', ip='{}'", username, action, ipAddress);
        AuditRecord record = new AuditRecord(username, action, details, ipAddress);
        record.setCreatedAt(LocalDateTime.now());
        auditRecordRepository.save(record);
    }

    @Transactional(readOnly = true)
    public List<AuditRecord> getAuditLog(String username) {
        log.info("Fetching audit log for username: '{}'", username);
        return auditRecordRepository.findByUsernameOrderByCreatedAtDesc(username);
    }
}
