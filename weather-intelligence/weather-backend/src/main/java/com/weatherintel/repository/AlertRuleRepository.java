package com.weatherintel.repository;

import com.weatherintel.entity.AlertRule;
import com.weatherintel.entity.enums.AlertType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AlertRuleRepository extends JpaRepository<AlertRule, Long> {

    List<AlertRule> findByUserIdAndEnabled(Long userId, boolean enabled);

    List<AlertRule> findByUserId(Long userId);

    List<AlertRule> findByCityId(Long cityId);

    List<AlertRule> findByCityIdAndEnabled(Long cityId, boolean enabled);

    List<AlertRule> findByAlertTypeAndEnabled(AlertType alertType, boolean enabled);
}
