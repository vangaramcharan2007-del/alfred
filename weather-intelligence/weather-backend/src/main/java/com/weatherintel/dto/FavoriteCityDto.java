package com.weatherintel.dto;

import java.time.LocalDateTime;

public class FavoriteCityDto {
    private Long id;
    private Long userId;
    private Long cityId;
    private String cityName;
    private String country;
    private double latitude;
    private double longitude;
    private int displayOrder;
    private String nickname;
    private LocalDateTime addedAt;

    public FavoriteCityDto() {
    }

    public FavoriteCityDto(Long id, Long userId, Long cityId, String cityName, String country,
                           double latitude, double longitude, int displayOrder, String nickname, LocalDateTime addedAt) {
        this.id = id;
        this.userId = userId;
        this.cityId = cityId;
        this.cityName = cityName;
        this.country = country;
        this.latitude = latitude;
        this.longitude = longitude;
        this.displayOrder = displayOrder;
        this.nickname = nickname;
        this.addedAt = addedAt;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
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

    public String getCountry() {
        return country;
    }

    public void setCountry(String country) {
        this.country = country;
    }

    public double getLatitude() {
        return latitude;
    }

    public void setLatitude(double latitude) {
        this.latitude = latitude;
    }

    public double getLongitude() {
        return longitude;
    }

    public void setLongitude(double longitude) {
        this.longitude = longitude;
    }

    public int getDisplayOrder() {
        return displayOrder;
    }

    public void setDisplayOrder(int displayOrder) {
        this.displayOrder = displayOrder;
    }

    public String getNickname() {
        return nickname;
    }

    public void setNickname(String nickname) {
        this.nickname = nickname;
    }

    public LocalDateTime getAddedAt() {
        return addedAt;
    }

    public void setAddedAt(LocalDateTime addedAt) {
        this.addedAt = addedAt;
    }
}
