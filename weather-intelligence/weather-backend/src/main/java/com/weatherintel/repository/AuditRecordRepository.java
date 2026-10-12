package com.weatherintel.repository;

import com.weatherintel.entity.AuditRecord;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AuditRecordRepository extends JpaRepository<AuditRecord, Long> {

    List<AuditRecord> findByUsernameOrderByCreatedAtDesc(String username);

    Page<AuditRecord> findByUsernameOrderByCreatedAtDesc(String username, Pageable pageable);
}
