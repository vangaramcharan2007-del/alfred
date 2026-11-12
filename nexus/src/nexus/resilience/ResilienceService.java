package nexus.resilience;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Enterprise Resilience Orchestrator - Circuit Breakers & Distributed Caching.
 * 
 * Author: Ram Charan Vanga (Reg No: RA2511027010164)
 * Department of Computer Science & Engineering
 * SRM Institute of Science and Technology, Kattankulathur
 */
public class ResilienceService {
    private static final ResilienceService instance = new ResilienceService();

    private final CircuitBreaker amazonBreaker;
    private final CircuitBreaker cryptoBreaker;
    private final CircuitBreaker weatherBreaker;
    private final List<CircuitBreaker> allBreakers = new ArrayList<>();

    private final ConcurrentLruCache<String, Object> memoryCache;

    private ResilienceService() {
        // Amazon Scraper: trip after 3 failures, 8-second cooldown
        amazonBreaker = new CircuitBreaker("Amazon India Scraper Pool", 3, 8000);
        // CoinGecko: trip after 3 failures, 6-second cooldown
        cryptoBreaker = new CircuitBreaker("CoinGecko Decentralized Rates", 3, 6000);
        // Weather: trip after 2 failures, 5-second cooldown
        weatherBreaker = new CircuitBreaker("SRM Kattankulathur Sensor Gateway", 2, 5000);

        allBreakers.add(amazonBreaker);
        allBreakers.add(cryptoBreaker);
        allBreakers.add(weatherBreaker);

        // LRU Cache: capacity 500 entries, default TTL 30 seconds
        memoryCache = new ConcurrentLruCache<>(500, 30000);
        seedInitialCache();
    }

    private void seedInitialCache() {
        memoryCache.put("market:laptop:top1", "HP 15 Intel Core 5 - Cached Fast Response");
        memoryCache.put("crypto:btc", 77950.0);
        memoryCache.put("crypto:eth", 2265.0);
        memoryCache.put("weather:srm", "26.2°C Partly Cloudy (Cached)");
        memoryCache.put("cinema:inox_potheri:dune", "Screen 1 IMAX Atmos (Cached)");
    }

    public static ResilienceService getInstance() {
        return instance;
    }

    public CircuitBreaker getAmazonBreaker() { return amazonBreaker; }
    public CircuitBreaker getCryptoBreaker() { return cryptoBreaker; }
    public CircuitBreaker getWeatherBreaker() { return weatherBreaker; }
    public List<CircuitBreaker> getAllBreakers() { return Collections.unmodifiableList(allBreakers); }
    public ConcurrentLruCache<String, Object> getMemoryCache() { return memoryCache; }

    public void simulateOutage(CircuitBreaker breaker) {
        if (breaker != null) {
            breaker.tripManually();
        }
    }

    public void recoverBreaker(CircuitBreaker breaker) {
        if (breaker != null) {
            breaker.reset();
        }
    }
}
