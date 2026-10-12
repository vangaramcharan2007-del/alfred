package com.weatherintel.dto;

import java.util.ArrayList;
import java.util.List;

public class ForecastResponse {

    private String cityName;
    private String country;
    private List<ForecastItemDto> forecasts = new ArrayList<>();

    public ForecastResponse() {
    }

    public ForecastResponse(String cityName, String country, List<ForecastItemDto> forecasts) {
        this.cityName = cityName;
        this.country = country;
        this.forecasts = forecasts != null ? forecasts : new ArrayList<>();
    }

    public String getCityName() {
        return cityName;
    }

    public void setCityName(String cityName) {
        this.cityName = cityName;
    }

    public String getCountry() {
        return country;
    }

    public void setCountry(String country) {
        this.country = country;
    }

    public List<ForecastItemDto> getForecasts() {
        return forecasts;
    }

    public void setForecasts(List<ForecastItemDto> forecasts) {
        this.forecasts = forecasts != null ? forecasts : new ArrayList<>();
    }
}
