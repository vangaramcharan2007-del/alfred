package com.weatherintel.dto;

public class ComparisonPeriodDto {
    private String periodLabel;
    private AnalyticsSummaryDto summary;
    private AnalyticsSummary period1;
    private AnalyticsSummary period2;
    private double tempDiff;
    private double humidityDiff;
    private double pressureDiff;
    private double windSpeedDiff;

    public ComparisonPeriodDto() {
    }

    public ComparisonPeriodDto(String periodLabel, AnalyticsSummaryDto summary) {
        this.periodLabel = periodLabel;
        this.summary = summary;
    }

    public ComparisonPeriodDto(AnalyticsSummary period1, AnalyticsSummary period2,
                               double tempDiff, double humidityDiff, double pressureDiff, double windSpeedDiff) {
        this.period1 = period1;
        this.period2 = period2;
        this.tempDiff = tempDiff;
        this.humidityDiff = humidityDiff;
        this.pressureDiff = pressureDiff;
        this.windSpeedDiff = windSpeedDiff;
        this.periodLabel = (period1 != null ? period1.getCityName() : "") + " Comparison";
    }

    public String getPeriodLabel() {
        return periodLabel;
    }

    public void setPeriodLabel(String periodLabel) {
        this.periodLabel = periodLabel;
    }

    public AnalyticsSummaryDto getSummary() {
        return summary;
    }

    public void setSummary(AnalyticsSummaryDto summary) {
        this.summary = summary;
    }

    public AnalyticsSummary getPeriod1() {
        return period1;
    }

    public void setPeriod1(AnalyticsSummary period1) {
        this.period1 = period1;
    }

    public AnalyticsSummary getPeriod2() {
        return period2;
    }

    public void setPeriod2(AnalyticsSummary period2) {
        this.period2 = period2;
    }

    public double getTempDiff() {
        return tempDiff;
    }

    public void setTempDiff(double tempDiff) {
        this.tempDiff = tempDiff;
    }

    public double getHumidityDiff() {
        return humidityDiff;
    }

    public void setHumidityDiff(double humidityDiff) {
        this.humidityDiff = humidityDiff;
    }

    public double getPressureDiff() {
        return pressureDiff;
    }

    public void setPressureDiff(double pressureDiff) {
        this.pressureDiff = pressureDiff;
    }

    public double getWindSpeedDiff() {
        return windSpeedDiff;
    }

    public void setWindSpeedDiff(double windSpeedDiff) {
        this.windSpeedDiff = windSpeedDiff;
    }
}
