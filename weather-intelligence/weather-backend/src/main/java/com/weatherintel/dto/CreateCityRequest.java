package com.weatherintel.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public class CreateCityRequest {
    @NotBlank(message = "City name cannot be blank")
    private String name;

    @NotBlank(message = "Country code or name cannot be blank")
    private String country;

    @NotNull(message = "Latitude is required")
    private Double lat;

    @NotNull(message = "Longitude is required")
    private Double lon;

    private String state;

    public CreateCityRequest() {
    }

    public CreateCityRequest(String name, String country, Double lat, Double lon, String state) {
        this.name = name;
        this.country = country;
        this.lat = lat;
        this.lon = lon;
        this.state = state;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getCountry() {
        return country;
    }

    public void setCountry(String country) {
        this.country = country;
    }

    public Double getLat() {
        return lat;
    }

    public void setLat(Double lat) {
        this.lat = lat;
    }

    public Double getLon() {
        return lon;
    }

    public void setLon(Double lon) {
        this.lon = lon;
    }

    public String getState() {
        return state;
    }

    public void setState(String state) {
        this.state = state;
    }
}
