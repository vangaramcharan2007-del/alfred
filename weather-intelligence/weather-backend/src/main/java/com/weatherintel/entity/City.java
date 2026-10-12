package com.weatherintel.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.time.LocalDateTime;
import java.util.Objects;

@Entity
@Table(name = "cities", indexes = {
        @Index(name = "idx_cities_name", columnList = "name"),
        @Index(name = "idx_cities_name_country", columnList = "name, country")
})
public class City {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank(message = "City name cannot be blank")
    @Column(name = "name", nullable = false, length = 100)
    private String name;

    @NotBlank(message = "Country code or name cannot be blank")
    @Column(name = "country", nullable = false, length = 10)
    private String country;

    @NotNull
    @Column(name = "latitude", nullable = false)
    private double latitude;

    @NotNull
    @Column(name = "longitude", nullable = false)
    private double longitude;

    @Column(name = "state", length = 100)
    private String state;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    public City() {
    }

    public City(Long id, String name, String country, double latitude, double longitude, String state) {
        this.id = id;
        this.name = name;
        this.country = country;
        this.latitude = latitude;
        this.longitude = longitude;
        this.state = state;
    }

    public City(String name, String country, double latitude, double longitude, String state) {
        this.name = name;
        this.country = country;
        this.latitude = latitude;
        this.longitude = longitude;
        this.state = state;
    }

    public City(String name, String country, double latitude, double longitude) {
        this(name, country, latitude, longitude, null);
    }

    @PrePersist
    protected void onCreate() {
        if (this.createdAt == null) {
            this.createdAt = LocalDateTime.now();
        }
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
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

    public String getState() {
        return state;
    }

    public void setState(String state) {
        this.state = state;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        City city = (City) o;
        return Objects.equals(id, city.id) ||
                (Double.compare(city.latitude, latitude) == 0 &&
                        Double.compare(city.longitude, longitude) == 0 &&
                        Objects.equals(name, city.name) &&
                        Objects.equals(country, city.country));
    }

    @Override
    public int hashCode() {
        return Objects.hash(id != null ? id : (name + country + latitude + longitude));
    }

    @Override
    public String toString() {
        return "City{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", country='" + country + '\'' +
                ", latitude=" + latitude +
                ", longitude=" + longitude +
                ", state='" + state + '\'' +
                ", createdAt=" + createdAt +
                '}';
    }
}
