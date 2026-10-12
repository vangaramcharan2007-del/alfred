package com.weatherintel.repository;

import com.weatherintel.entity.City;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface CityRepository extends JpaRepository<City, Long> {

    List<City> findByNameContainingIgnoreCase(String name);

    Optional<City> findByNameAndCountry(String name, String country);

    Optional<City> findFirstByNameIgnoreCaseAndCountryIgnoreCase(String name, String country);
}
