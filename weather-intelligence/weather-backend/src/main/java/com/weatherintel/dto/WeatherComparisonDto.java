package com.weatherintel.dto;

import java.util.ArrayList;
import java.util.List;

public class WeatherComparisonDto {

    private List<WeatherResponse> cities = new ArrayList<>();

    public WeatherComparisonDto() {
    }

    public WeatherComparisonDto(List<WeatherResponse> cities) {
        this.cities = cities != null ? cities : new ArrayList<>();
    }

    public List<WeatherResponse> getCities() {
        return cities;
    }

    public void setCities(List<WeatherResponse> cities) {
        this.cities = cities != null ? cities : new ArrayList<>();
    }
}
