package com.weatherintel.entity;

import jakarta.persistence.*;

import java.time.LocalDateTime;
import java.util.Objects;

@Entity
@Table(name = "favorite_cities", uniqueConstraints = {
        @UniqueConstraint(name = "uk_favorite_user_city", columnNames = {"user_id", "city_id"})
}, indexes = {
        @Index(name = "idx_favorite_user_id", columnList = "user_id"),
        @Index(name = "idx_favorite_city_id", columnList = "city_id")
})
public class FavoriteCity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @ManyToOne(fetch = FetchType.EAGER, optional = false)
    @JoinColumn(name = "city_id", nullable = false)
    private City city;

    @Column(name = "display_order", nullable = false)
    private int displayOrder = 0;

    @Column(name = "nickname", length = 100)
    private String nickname;

    @Column(name = "added_at", nullable = false, updatable = false)
    private LocalDateTime addedAt;

    public FavoriteCity() {
    }

    public FavoriteCity(Long id, User user, City city, int displayOrder, String nickname) {
        this.id = id;
        this.user = user;
        this.city = city;
        this.displayOrder = displayOrder;
        this.nickname = nickname;
    }

    public FavoriteCity(User user, City city, int displayOrder, String nickname) {
        this.user = user;
        this.city = city;
        this.displayOrder = displayOrder;
        this.nickname = nickname;
    }

    @PrePersist
    protected void onCreate() {
        if (this.addedAt == null) {
            this.addedAt = LocalDateTime.now();
        }
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public User getUser() {
        return user;
    }

    public void setUser(User user) {
        this.user = user;
    }

    public City getCity() {
        return city;
    }

    public void setCity(City city) {
        this.city = city;
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

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        FavoriteCity that = (FavoriteCity) o;
        return Objects.equals(id, that.id) ||
                (user != null && that.user != null && Objects.equals(user.getId(), that.user.getId()) &&
                        city != null && that.city != null && Objects.equals(city.getId(), that.city.getId()));
    }

    @Override
    public int hashCode() {
        return Objects.hash(id != null ? id : (user != null && city != null ? Objects.hash(user.getId(), city.getId()) : 0));
    }

    @Override
    public String toString() {
        return "FavoriteCity{" +
                "id=" + id +
                ", userId=" + (user != null ? user.getId() : null) +
                ", cityId=" + (city != null ? city.getId() : null) +
                ", displayOrder=" + displayOrder +
                ", nickname='" + nickname + '\'' +
                ", addedAt=" + addedAt +
                '}';
    }
}
