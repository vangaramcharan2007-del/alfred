package com.weatherintel.repository;

import com.weatherintel.entity.ForecastEntry;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface ForecastEntryRepository extends JpaRepository<ForecastEntry, Long> {

    List<ForecastEntry> findByCityIdAndForecastTimeAfterOrderByForecastTimeAsc(Long cityId, LocalDateTime forecastTime);

    @Modifying
    @Query("DELETE FROM ForecastEntry f WHERE f.city.id = :cityId AND f.createdAt < :cutoff")
    void deleteByCityIdAndCreatedAtBefore(@Param("cityId") Long cityId, @Param("cutoff") LocalDateTime cutoff);

    @Modifying
    @Query("DELETE FROM ForecastEntry f WHERE f.city.id = :cityId")
    void deleteByCityId(@Param("cityId") Long cityId);
}
