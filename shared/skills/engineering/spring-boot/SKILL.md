---
name: spring-boot
description: Build and maintain Spring Boot applications following modern backend engineering practices.
---

# Spring Boot Engineering

## Technology baseline

- Java 21+
- Spring Boot 3.x+
- Maven
- Constructor injection
- Jakarta Validation
- Spring Data JPA
- Flyway
- Testcontainers

## General rules

- Controllers must not contain business logic
- Transactions belong in application/service layer
- Domain layer must not depend on infrastructure
- Prefer immutable DTOs
- Prefer records when appropriate
- Avoid field injection
- Never expose JPA entities directly through REST APIs