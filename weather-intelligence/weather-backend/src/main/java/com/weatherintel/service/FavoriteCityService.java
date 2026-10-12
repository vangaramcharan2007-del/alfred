package com.weatherintel.service;

import com.weatherintel.entity.City;
import com.weatherintel.entity.FavoriteCity;
import com.weatherintel.entity.User;
import com.weatherintel.exception.ResourceNotFoundException;
import com.weatherintel.repository.CityRepository;
import com.weatherintel.repository.FavoriteCityRepository;
import com.weatherintel.repository.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
public class FavoriteCityService {

    private static final Logger log = LoggerFactory.getLogger(FavoriteCityService.class);

    private final FavoriteCityRepository favoriteCityRepository;
    private final UserRepository userRepository;
    private final CityRepository cityRepository;

    public FavoriteCityService(FavoriteCityRepository favoriteCityRepository,
                               UserRepository userRepository,
                               CityRepository cityRepository) {
        this.favoriteCityRepository = favoriteCityRepository;
        this.userRepository = userRepository;
        this.cityRepository = cityRepository;
    }

    @Transactional(readOnly = true)
    public List<FavoriteCity> getFavorites(Long userId) {
        log.info("Fetching favorites for userId: {}", userId);
        return favoriteCityRepository.findByUserIdOrderByDisplayOrderAsc(userId);
    }

    @Transactional
    public FavoriteCity addFavorite(Long userId, Long cityId) {
        log.info("Adding favorite cityId: {} for userId: {}", cityId, userId);
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User", "id", userId));
        City city = cityRepository.findById(cityId)
                .orElseThrow(() -> new ResourceNotFoundException("City", "id", cityId));

        Optional<FavoriteCity> existing = favoriteCityRepository.findByUserIdAndCityId(userId, cityId);
        if (existing.isPresent()) {
            return existing.get();
        }

        long count = favoriteCityRepository.countByUserId(userId);
        FavoriteCity favoriteCity = new FavoriteCity(user, city, (int) count, null);
        return favoriteCityRepository.save(favoriteCity);
    }

    @Transactional
    public void removeFavorite(Long userId, Long cityId) {
        log.info("Removing favorite cityId: {} for userId: {}", cityId, userId);
        favoriteCityRepository.deleteByUserIdAndCityId(userId, cityId);
    }

    @Transactional
    public void reorderFavorites(Long userId, List<Long> orderedCityIds) {
        log.info("Reordering favorites for userId: {}", userId);
        if (orderedCityIds == null || orderedCityIds.isEmpty()) {
            return;
        }

        for (int i = 0; i < orderedCityIds.size(); i++) {
            Long cityId = orderedCityIds.get(i);
            Optional<FavoriteCity> favOpt = favoriteCityRepository.findByUserIdAndCityId(userId, cityId);
            if (favOpt.isPresent()) {
                FavoriteCity fav = favOpt.get();
                fav.setDisplayOrder(i);
                favoriteCityRepository.save(fav);
            }
        }
    }

    @Transactional
    public FavoriteCity updateNickname(Long userId, Long cityId, String nickname) {
        log.info("Updating nickname for cityId: {} and userId: {} to '{}'", cityId, userId, nickname);
        FavoriteCity favoriteCity = favoriteCityRepository.findByUserIdAndCityId(userId, cityId)
                .orElseThrow(() -> new ResourceNotFoundException("FavoriteCity not found for user " + userId + " and city " + cityId));
        favoriteCity.setNickname(nickname);
        return favoriteCityRepository.save(favoriteCity);
    }
}
