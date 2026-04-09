# ADR-001: Database Selection - MySQL 8.0

## Status

ACCEPTED

## Context

BookMyJuice requires a relational database to store:
- User accounts and authentication data
- Subscription records (synced with Chargebee)
- Order history
- Product catalog (synced with Chargebee)
- Address books
- Audit logs

Key requirements:
- ACID compliance for financial transactions
- Strong consistency for subscription and order data
- Integration with Spring Boot / Hibernate
- Support for complex queries and reporting
- Familiarity for the development team
- Cost-effective for startup phase

## Decision

We selected **MySQL 8.0** as our primary database.

### Rationale

1. **Team Expertise**: The development team has extensive MySQL experience
2. **Spring Boot Integration**: Excellent support via Spring Data JPA
3. **Cost**: Free and open-source (Community Edition)
4. **Performance**: Sufficient for expected scale (millions of rows)
5. **Chargebee Compatibility**: Chargebee webhooks map well to MySQL structure
6. **JSON Support**: MySQL 8.0 has improved JSON functionality for flexible schemas
7. **Cloud Options**: Easy to migrate to managed MySQL (RDS, Cloud SQL) later

### Alternatives Considered

**PostgreSQL:**
- Pros: More advanced features, better JSON support
- Cons: Team less familiar, marginal benefit for our use case
- Verdict: Good alternative, but MySQL sufficient

**MongoDB:**
- Pros: Flexible schema, good for rapid iteration
- Cons: Not ideal for transactional data, eventual consistency concerns
- Verdict: Rejected for core data, may use for analytics later

**DynamoDB:**
- Pros: Fully managed, auto-scaling
- Cons: Vendor lock-in, complex queries difficult, eventual consistency
- Verdict: Rejected for primary database

## Consequences

### Positive

- Fast development with familiar technology
- Strong data integrity for financial transactions
- Easy to find developers with MySQL skills
- Good documentation and community support

### Negative

- Manual scaling required (vs. managed services)
- Need to manage backups and replication ourselves
- May need to migrate to managed MySQL at scale

### Risks

- **Single Point of Failure**: Mitigated by regular backups
- **Scaling Limits**: Will hit limits at ~10M rows, plan to shard or migrate
- **Operational Overhead**: Team needs to manage DB administration

## Implementation

- MySQL 8.0 via Docker for local development
- Production: AWS RDS MySQL or similar managed service
- Flyway for database migrations
- Connection pooling via HikariCP
- Read replicas for reporting queries (future)

## References

- [MySQL 8.0 Documentation](https://dev.mysql.com/doc/refman/8.0/en/)
- [Spring Data JPA](https://spring.io/projects/spring-data-jpa)
- [Flyway Migrations](https://flywaydb.org/)

---

*Date: 2026-03-27*
*Authors: BookMyJuice Engineering Team*
