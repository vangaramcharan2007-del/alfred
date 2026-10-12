package com.weatherintel.dto;

import jakarta.validation.constraints.NotNull;

import java.time.LocalDate;

public class HistoricalDataRequest {

    @NotNull(message = "City ID is required")
    private Long cityId;

    @NotNull(message = "Start date is required")
    private LocalDate startDate;

    @NotNull(message = "End date is required")
    private LocalDate endDate;

    public HistoricalDataRequest() {
    }

    public HistoricalDataRequest(Long cityId, LocalDate startDate, LocalDate endDate) {
        this.cityId = cityId;
        this.startDate = startDate;
        this.endDate = endDate;
    }

    public Long getCityId() {
        return cityId;
    }

    public void setCityId(Long cityId) {
        this.cityId = cityId;
    }

    public LocalDate getStartDate() {
        return startDate;
    }

    public void setStartDate(LocalDate startDate) {
        this.startDate = startDate;
    }

    public LocalDate getEndDate() {
        return endDate;
    }

    public void setEndDate(LocalDate endDate) {
        this.endDate = endDate;
    }
}
