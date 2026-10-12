package com.weatherintel.controller;

import com.weatherintel.dto.AddFavoriteRequest;
import com.weatherintel.dto.FavoriteCityDto;
import com.weatherintel.dto.FavoriteNicknameRequest;
import com.weatherintel.dto.ReorderFavoritesRequest;
import com.weatherintel.service.FavoriteCityService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/favorites")
public class FavoriteCityController {

    private final FavoriteCityService favoriteCityService;

    public FavoriteCityController(FavoriteCityService favoriteCityService) {
        this.favoriteCityService = favoriteCityService;
    }

    @GetMapping
    public ResponseEntity<List<FavoriteCityDto>> getFavorites(@RequestParam("userId") Long userId) {
        List<com.weatherintel.entity.FavoriteCity> favorites = favoriteCityService.getFavorites(userId);
        return ResponseEntity.ok(favorites.stream().map(this::toDto).toList());
    }

    @PostMapping
    public ResponseEntity<FavoriteCityDto> addFavorite(@Valid @RequestBody AddFavoriteRequest request) {
        com.weatherintel.entity.FavoriteCity created = favoriteCityService.addFavorite(request.getUserId(), request.getCityId());
        return new ResponseEntity<>(toDto(created), HttpStatus.CREATED);
    }

    @DeleteMapping
    public ResponseEntity<Void> removeFavorite(@RequestParam("userId") Long userId,
                                                @RequestParam("cityId") Long cityId) {
        favoriteCityService.removeFavorite(userId, cityId);
        return ResponseEntity.noContent().build();
    }

    @PutMapping("/reorder")
    public ResponseEntity<Void> reorderFavorites(@RequestBody ReorderFavoritesRequest request) {
        favoriteCityService.reorderFavorites(request.getUserId(), request.getOrderedCityIds());
        return ResponseEntity.ok().build();
    }

    @PutMapping("/nickname")
    public ResponseEntity<FavoriteCityDto> updateNickname(@RequestBody FavoriteNicknameRequest request) {
        com.weatherintel.entity.FavoriteCity updated = favoriteCityService.updateNickname(
                request.getUserId(),
                request.getCityId(),
                request.getNickname()
        );
        return ResponseEntity.ok(toDto(updated));
    }

    private FavoriteCityDto toDto(com.weatherintel.entity.FavoriteCity f) {
        if (f == null) return null;
        return new FavoriteCityDto(
                f.getId(),
                f.getUser() != null ? f.getUser().getId() : null,
                f.getCity() != null ? f.getCity().getId() : null,
                f.getCity() != null ? f.getCity().getName() : null,
                f.getCity() != null ? f.getCity().getCountry() : null,
                f.getCity() != null ? f.getCity().getLatitude() : 0.0,
                f.getCity() != null ? f.getCity().getLongitude() : 0.0,
                f.getDisplayOrder(),
                f.getNickname(),
                f.getAddedAt()
        );
    }
}
