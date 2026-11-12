package nexus.resilience;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.locks.ReentrantReadWriteLock;

/**
 * Thread-Safe In-Memory LRU Cache with TTL Expiration & Performance Counters.
 * 
 * Author: Ram Charan Vanga (Reg No: RA2511027010164)
 * Department of Computer Science & Engineering
 * SRM Institute of Science and Technology, Kattankulathur
 */
public class ConcurrentLruCache<K, V> {
    private final int maxCapacity;
    private final long defaultTtlMs;
    private final Map<K, CacheEntry<V>> map;
    private final ReentrantReadWriteLock lock = new ReentrantReadWriteLock();

    private final AtomicLong hitCount = new AtomicLong(0);
    private final AtomicLong missCount = new AtomicLong(0);
    private final AtomicLong evictionCount = new AtomicLong(0);

    private static class CacheEntry<V> {
        final V value;
        final long expiresAt;

        CacheEntry(V value, long ttlMs) {
            this.value = value;
            this.expiresAt = System.currentTimeMillis() + ttlMs;
        }

        boolean isExpired() {
            return System.currentTimeMillis() > expiresAt;
        }
    }

    public ConcurrentLruCache(int maxCapacity, long defaultTtlMs) {
        this.maxCapacity = maxCapacity;
        this.defaultTtlMs = defaultTtlMs;
        this.map = new LinkedHashMap<K, CacheEntry<V>>(maxCapacity, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry<K, CacheEntry<V>> eldest) {
                if (size() > ConcurrentLruCache.this.maxCapacity) {
                    evictionCount.incrementAndGet();
                    return true;
                }
                return false;
            }
        };
    }

    public V get(K key) {
        lock.readLock().lock();
        try {
            CacheEntry<V> entry = map.get(key);
            if (entry != null && !entry.isExpired()) {
                hitCount.incrementAndGet();
                return entry.value;
            }
        } finally {
            lock.readLock().unlock();
        }

        missCount.incrementAndGet();
        return null;
    }

    public void put(K key, V value) {
        put(key, value, defaultTtlMs);
    }

    public void put(K key, V value, long ttlMs) {
        lock.writeLock().lock();
        try {
            map.put(key, new CacheEntry<>(value, ttlMs));
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void clear() {
        lock.writeLock().lock();
        try {
            map.clear();
        } finally {
            lock.writeLock().unlock();
        }
    }

    public int size() {
        lock.readLock().lock();
        try {
            return map.size();
        } finally {
            lock.readLock().unlock();
        }
    }

    public long getHitCount() { return hitCount.get(); }
    public long getMissCount() { return missCount.get(); }
    public long getEvictionCount() { return evictionCount.get(); }

    public double getHitRatio() {
        long total = hitCount.get() + missCount.get();
        return total == 0 ? 0.0 : ((double) hitCount.get() / total) * 100.0;
    }
}
