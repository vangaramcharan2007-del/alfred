package com.weatherintel.repository;

import com.weatherintel.entity.FavoriteCity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface FavoriteCityRepository extends JpaRepository<FavoriteCity, Long> {

    List<FavoriteCity> findByUserIdOrderByDisplayOrderAsc(Long userId);

    List<FavoriteCity> findByUserIdOrderByDisplayOrder(Long userId);

    Optional<FavoriteCity> findByUserIdAndCityId(Long userId, Long cityId);

    @Modifying
    @Query("DELETE FROM FavoriteCity f WHERE f.user.id = :userId AND f.city.id = :cityId")
    void deleteByUserIdAndCityId(@Param("userId") Long userId, @Param("cityId") Long cityId);

    long countByUserId(Long userId);
}
