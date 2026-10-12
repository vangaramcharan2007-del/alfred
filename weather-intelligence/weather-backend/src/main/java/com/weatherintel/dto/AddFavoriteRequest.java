package com.weatherintel.dto;

import jakarta.validation.constraints.NotNull;

public class AddFavoriteRequest {
    @NotNull(message = "User ID is required")
    private Long userId;

    @NotNull(message = "City ID is required")
    private Long cityId;

    public AddFavoriteRequest() {
    }

    public AddFavoriteRequest(Long userId, Long cityId) {
        this.userId = userId;
        this.cityId = cityId;
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
}
