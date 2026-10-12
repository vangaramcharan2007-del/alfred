package com.weatherintel.dto;

import java.time.LocalDate;

public class AnalyticsSummary {

    private String cityName;
    private LocalDate periodStart;
    private LocalDate periodEnd;
    private double avgTemp;
    private double minTemp;
    private double maxTemp;
    private double avgHumidity;
    private double avgPressure;
    private double avgWindSpeed;
    private int totalReadings;

    public AnalyticsSummary() {
    }

    public AnalyticsSummary(String cityName, LocalDate periodStart, LocalDate periodEnd,
                            double avgTemp, double minTemp, double maxTemp,
                            double avgHumidity, double avgPressure, double avgWindSpeed,
                            int totalReadings) {
        this.cityName = cityName;
        this.periodStart = periodStart;
        this.periodEnd = periodEnd;
        this.avgTemp = avgTemp;
        this.minTemp = minTemp;
        this.maxTemp = maxTemp;
        this.avgHumidity = avgHumidity;
        this.avgPressure = avgPressure;
        this.avgWindSpeed = avgWindSpeed;
        this.totalReadings = totalReadings;
    }

    public String getCityName() {
        return cityName;
    }

    public void setCityName(String cityName) {
        this.cityName = cityName;
    }

    public LocalDate getPeriodStart() {
        return periodStart;
    }

    public void setPeriodStart(LocalDate periodStart) {
        this.periodStart = periodStart;
    }

    public LocalDate getPeriodEnd() {
        return periodEnd;
    }

    public void setPeriodEnd(LocalDate periodEnd) {
        this.periodEnd = periodEnd;
    }

    public double getAvgTemp() {
        return avgTemp;
    }

    public void setAvgTemp(double avgTemp) {
        this.avgTemp = avgTemp;
    }

    public double getMinTemp() {
        return minTemp;
    }

    public void setMinTemp(double minTemp) {
        this.minTemp = minTemp;
    }

    public double getMaxTemp() {
        return maxTemp;
    }

    public void setMaxTemp(double maxTemp) {
        this.maxTemp = maxTemp;
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

    public void setPressure(double avgPressure) {
        this.avgPressure = avgPressure;
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

    public int getTotalReadings() {
        return totalReadings;
    }

    public void setTotalReadings(int totalReadings) {
        this.totalReadings = totalReadings;
    }
}
