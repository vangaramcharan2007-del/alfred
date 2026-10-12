package com.weatherintel.repository;

import com.weatherintel.entity.WeatherSnapshot;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.Collection;
import java.util.List;
import java.util.Optional;

@Repository
public interface WeatherSnapshotRepository extends JpaRepository<WeatherSnapshot, Long> {

    Optional<WeatherSnapshot> findTopByCityIdOrderByRecordedAtDesc(Long cityId);

    Page<WeatherSnapshot> findByCityIdAndRecordedAtBetween(Long cityId, LocalDateTime start, LocalDateTime end, Pageable pageable);

    List<WeatherSnapshot> findByCityIdAndRecordedAtBetweenOrderByRecordedAtAsc(Long cityId, LocalDateTime start, LocalDateTime end);

    List<WeatherSnapshot> findByCityIdIn(Collection<Long> cityIds);
}
