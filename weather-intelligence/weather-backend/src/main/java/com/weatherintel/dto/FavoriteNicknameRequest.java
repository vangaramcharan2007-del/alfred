package com.weatherintel.dto;

public class FavoriteNicknameRequest {
    private Long userId;
    private Long cityId;
    private String nickname;

    public FavoriteNicknameRequest() {
    }

    public FavoriteNicknameRequest(Long userId, Long cityId, String nickname) {
        this.userId = userId;
        this.cityId = cityId;
        this.nickname = nickname;
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

    public String getNickname() {
        return nickname;
    }

    public void setNickname(String nickname) {
        this.nickname = nickname;
    }
}
