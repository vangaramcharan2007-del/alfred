package com.weatherintel.dto;

import java.util.List;

public class ReorderFavoritesRequest {
    private Long userId;
    private List<Long> orderedCityIds;

    public ReorderFavoritesRequest() {
    }

    public ReorderFavoritesRequest(Long userId, List<Long> orderedCityIds) {
        this.userId = userId;
        this.orderedCityIds = orderedCityIds;
    }

    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public List<Long> getOrderedCityIds() {
        return orderedCityIds;
    }

    public void setOrderedCityIds(List<Long> orderedCityIds) {
        this.orderedCityIds = orderedCityIds;
    }
}
