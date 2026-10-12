package com.weatherintel.dto;

import java.util.Map;

public class AnalyticsSummaryDto {
    private Long cityId;
    private String cityName;
    private double avgTemperature;
    private double minTemperature;
    private double maxTemperature;
    private double avgHumidity;
    private double avgPressure;
    private double avgWindSpeed;
    private long totalRecords;
    private Map<String, Long> weatherConditionsCount;

    public AnalyticsSummaryDto() {
    }

    public AnalyticsSummaryDto(Long cityId, String cityName, double avgTemperature, double minTemperature,
                               double maxTemperature, double avgHumidity, double avgPressure,
                               double avgWindSpeed, long totalRecords, Map<String, Long> weatherConditionsCount) {
        this.cityId = cityId;
        this.cityName = cityName;
        this.avgTemperature = avgTemperature;
        this.minTemperature = minTemperature;
        this.maxTemperature = maxTemperature;
        this.avgHumidity = avgHumidity;
        this.avgPressure = avgPressure;
        this.avgWindSpeed = avgWindSpeed;
        this.totalRecords = totalRecords;
        this.weatherConditionsCount = weatherConditionsCount;
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

    public double getAvgTemperature() {
        return avgTemperature;
    }

    public void setAvgTemperature(double avgTemperature) {
        this.avgTemperature = avgTemperature;
    }

    public double getMinTemperature() {
        return minTemperature;
    }

    public void setMinTemperature(double minTemperature) {
        this.minTemperature = minTemperature;
    }

    public double getMaxTemperature() {
        return maxTemperature;
    }

    public void setMaxTemperature(double maxTemperature) {
        this.maxTemperature = maxTemperature;
    }

    public double getAvgHumidity() {
        return avgHumidity;
    }

    public void setAvgHumidity(double avgHumidity) {
        this.avgHumidity = avgHumidity;
    }

    public double getAvgPressure() {
        return avgPressure;
    }

    public void setAvgPressure(double avgPressure) {
        this.avgPressure = avgPressure;
    }

    public double getAvgWindSpeed() {
        return avgWindSpeed;
    }

    public void setAvgWindSpeed(double avgWindSpeed) {
        this.avgWindSpeed = avgWindSpeed;
    }

    public long getTotalRecords() {
        return totalRecords;
    }

    public void setTotalRecords(long totalRecords) {
        this.totalRecords = totalRecords;
    }

    public Map<String, Long> getWeatherConditionsCount() {
        return weatherConditionsCount;
    }

    public void setWeatherConditionsCount(Map<String, Long> weatherConditionsCount) {
        this.weatherConditionsCount = weatherConditionsCount;
    }
}
