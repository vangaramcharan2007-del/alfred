package com.weatherintel.controller;

import com.weatherintel.dto.AlertRuleDto;
import com.weatherintel.service.AlertService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/alerts")
public class AlertController {

    private final AlertService alertService;

    public AlertController(AlertService alertService) {
        this.alertService = alertService;
    }

    @GetMapping
    public ResponseEntity<List<AlertRuleDto>> getAlerts(@RequestParam("userId") Long userId) {
        List<AlertRuleDto> rules = alertService.getAlertRules(userId);
        return ResponseEntity.ok(rules);
    }

    @PostMapping
    public ResponseEntity<AlertRuleDto> createAlert(@Valid @RequestBody AlertRuleDto alertRuleDto,
                                                    @RequestParam(value = "userId", required = false) Long userIdParam) {
        Long userId = (userIdParam != null) ? userIdParam : alertRuleDto.getUserId();
        if (userId == null) {
            throw new IllegalArgumentException("userId must be provided either as parameter or in request body");
        }
        AlertRuleDto created = alertService.createAlertRule(userId, alertRuleDto);
        return new ResponseEntity<>(created, HttpStatus.CREATED);
    }

    @PutMapping("/{id}")
    public ResponseEntity<AlertRuleDto> updateAlert(@PathVariable("id") Long id,
                                                    @Valid @RequestBody AlertRuleDto alertRuleDto) {
        AlertRuleDto updated = alertService.updateAlertRule(id, alertRuleDto);
        return ResponseEntity.ok(updated);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteAlert(@PathVariable("id") Long id) {
        alertService.deleteAlertRule(id);
        return ResponseEntity.noContent().build();
    }
}
