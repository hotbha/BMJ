# Caching Strategy - BookMyJuice

**Version:** 2.0
**Last Updated:** 2026-05-08

---

## Overview

Caching strategy with **Implemented** vs **Planned** sections.

---

## IMPLEMENTED - Spring Caching Annotations

- @Cacheable and @CacheEvict placed on ItemService, PlanService, CustomerService
- Design: Cache-aside pattern (check cache, DB fallback, populate on miss)
- NOTE: No RedisConfig or CacheService exists yet. Annotations defined but non-functional until a cache provider is configured.

---

## PLANNED - Redis Cache Infrastructure

### 1. RedisConfig.java
@Configuration + @EnableCaching, RedisTemplate with StringRedisSerializer, Jackson2JsonRedisSerializer.
Status: Not implemented.

### 2. CacheService.java
evictProducts, evictPlans, evictCustomerData, evictByPattern.
Status: Not implemented.

### 3. CacheWarmupService
@Component + InitializingBean. Warms caches on startup (prod/staging only).
Status: Not implemented.

### 4. TTL Policies
products/plans/prices: 15min, serviceAreas: 24h, deliverySlots: 2min, customer:*: 5min.
Status: Not configured.

### 5. Graceful Degradation
Fall back to MySQL, log warning, report via health endpoint, auto-recover.
Status: Not implemented.

### 6. Monitoring
Hit ratio >80%, miss latency <5ms, mem <75%, pool <80%.
Status: Not implemented.

---

## Dependency Required

Add to bmjServer/pom.xml (not currently present):

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

---

## Testing Status

All cache tests (hit, miss, evict, graceful degradation, TTL): Not implemented.
