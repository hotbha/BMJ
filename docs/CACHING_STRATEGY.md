# Caching Strategy — BookMyJuice

**Document Version:** 1.0  
**Last Updated:** 2026-05-08

---

## 1. Cache Architecture

```
Flutter App ──► bmjServer ──► Redis Cache ──► MySQL
                                    │
                                    │
                              Webhook Eviction
                                    │
                                    ▼
                              Chargebee Events
```

- **Redis** is the primary application cache (in-memory).
- **MySQL** is the persistent read store (local cache of Chargebee data).
- **Cache-aside pattern**: Check Redis first, fall back to MySQL, populate Redis on miss.
- **TTL-based expiry** with webhook-driven eviction for near-real-time updates.

---

## 2. Technical Stack

| Layer | Technology | Configuration |
|-------|------------|---------------|
| Cache Abstraction | Spring Cache (`@Cacheable`, `@CacheEvict`) | Spring Boot starter-cache |
| Cache Store | Redis 7.x | spring-boot-starter-data-redis |
| Serialization | JSON (Jackson2JsonRedisSerializer) | Via RedisTemplate |
| Connection | Lettuce (non-blocking, reactive) | Redis auto-configuration |

---

## 3. TTL Policies by Domain

| Cache Name | Key Pattern | TTL | Why | Staleness Tolerance |
|------------|-------------|-----|-----|---------------------|
| `products` | `products:{id}` | 15 minutes | Product catalog changes infrequently | Low |
| `products:all` | `products:all` | 15 minutes | Full product list | Low |
| `plans` | `plans:{id}` | 15 minutes | Plan data changes rarely | Low |
| `plans:all` | `plans:all` | 15 minutes | All subscription plans | Low |
| `prices` | `prices:{id}` | 15 minutes | Item prices | Low |
| `serviceAreas` | `serviceAreas:{pincode}` | 24 hours | Serviceability data changes rarely | Medium |
| `deliverySlots` | `deliverySlots:{date}:{area}` | 2 minutes | Slots update frequently, needs freshness | Critical |
| `customer:subscriptions` | `customer:{customerId}:subscriptions` | 5 minutes | Per-user subscription cache | Medium |
| `customer:invoices` | `customer:{customerId}:invoices` | 5 minutes | Per-user invoice cache | Medium |
| `customer:orders` | `customer:{customerId}:orders` | 5 minutes | Per-user order cache | Medium |

---

## 4. Cache Namespace

```
bookmyjuice:products:{id}
bookmyjuice:plans:{id}
bookmyjuice:serviceAreas:{pincode}
bookmyjuice:deliverySlots:{date}:{area}
bookmyjuice:customer:{customerId}:subscriptions
```

Namespace prefix `bookmyjuice:` allows multiple environments to share a single Redis instance safely (dev/staging/prod).

---

## 5. Cache Warmup

On application startup, the `ChargebeeSyncService` can optionally warm the cache:

```java
@Component
public class CacheWarmupService implements InitializingBean {
    
    @Override
    public void afterPropertiesSet() {
        if (env.acceptsProfiles(Profiles.of("production", "staging"))) {
            warmupCaches();
        }
    }
    
    private void warmupCaches() {
        // Warm: products, plans, service areas
        productService.getAllProducts();   // Populates Redis
        planService.getAllPlans();         // Populates Redis
        deliveryService.getAllServiceAreas(); // Populates Redis
    }
}
```

---

## 6. Cache Eviction (Webhook-Driven)

When Chargebee sends a webhook event, affected cache entries are evicted:

```java
@Service
public class CacheService {
    
    @Autowired
    private CacheManager cacheManager;
    
    public void evictProducts() {
        cacheManager.getCache("products").clear();
    }
    
    public void evictPlans() {
        cacheManager.getCache("plans").clear();
    }
    
    public void evictCustomerData(String customerId) {
        evictByPattern("customer:" + customerId + ":*");
    }
    
    private void evictByPattern(String pattern) {
        // Use Redis keys command with pattern
        Set<String> keys = redisTemplate.keys("bookmyjuice:" + pattern);
        if (keys != null && !keys.isEmpty()) {
            redisTemplate.delete(keys);
        }
    }
}
```

---

## 7. Graceful Degradation

If Redis is unavailable:

1. **Cache miss behavior**: Fall back to MySQL query
2. **Circuit breaker**: Skip cache entirely, log warning
3. **No cascading failures**: Each request hits DB directly
4. **Health check**: `GET /api/health` reports Redis status
5. **Auto-recovery**: When Redis comes back, caching resumes at next request

```yaml
# application.yml
spring:
  cache:
    type: redis
  redis:
    host: ${REDIS_HOST:localhost}
    port: ${REDIS_PORT:6379}
    timeout: 2000ms
    connect-timeout: 1000ms
    lettuce:
      pool:
        max-active: 8
        max-idle: 4
        min-idle: 1
```

---

## 8. Configuration Properties

```properties
# Redis Cache Configuration
spring.cache.type=redis
spring.cache.redis.time-to-live=900000  # 15 minutes default TTL (ms)
spring.cache.redis.cache-null-values=false
spring.cache.redis.key-prefix=bookmyjuice:
spring.cache.redis.use-key-prefix=true

# Redis Connection
spring.data.redis.host=${REDIS_HOST:localhost}
spring.data.redis.port=${REDIS_PORT:6379}
spring.data.redis.timeout=2000ms
spring.data.redis.lettuce.pool.max-active=8
spring.data.redis.lettuce.pool.max-idle=4
spring.data.redis.lettuce.pool.min-idle=1
```

---

## 9. Monitoring

| Metric | Check |
|--------|-------|
| Cache hit ratio | > 80% for products, plans |
| Cache miss latency | < 5ms for Redis, < 50ms for MySQL fallback |
| Eviction rate | Tracked via Spring Actuator |
| Redis memory usage | < 75% of allocated maxmemory |
| Connection pool usage | < 80% active connections |

---

## 10. Testing

| Test | Type | Description |
|------|------|-------------|
| Cache hit returns data | Unit | @Cacheable method returns cached value |
| Cache miss fetches from DB | Unit | @Cacheable method hits DB on first call |
| Cache eviction works | Integration | @CacheEvict removes entry |
| Graceful degradation | Integration | Stop Redis, verify fallback to DB |
| TTL expiry | Integration | Data expires after configured TTL |
| Concurrent cache access | Integration | Multiple threads don't cause issues |

---

**Document Maintained By:** Engineering Team  
**Last Review:** 2026-05-08  
**Next Review:** 2026-06-08
