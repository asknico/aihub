---
name: spring-boot-ddd
description: >
  Build and refactor Spring Boot projects using DDD (Domain-Driven Design)
  layering. Use when creating a new Spring Boot service with DDD structure,
  migrating a traditional MVC project to DDD, designing aggregates, entities,
  value objects, domain events and repositories, or reviewing DDD compliance.
  使用 DDD 分层架构搭建或重构 Spring Boot 项目：限界上下文、聚合、实体、
  值对象、领域事件、仓储接口与依赖倒置。
---

# Spring Boot DDD

## When to use

Use this skill when:

- creating a new Spring Boot service with DDD layering
- migrating a traditional MVC / three-layer project to DDD
- designing aggregates, entities, value objects, domain events
- defining repository interfaces with dependency inversion
- reviewing existing code for DDD layering compliance

使用场景：新建 DDD 风格的 Spring Boot 服务；将三层/MVC 项目重构为 DDD；
设计聚合与领域模型；评审代码的 DDD 分层合规性。

## Standard module structure

```
com.example.order
├── interfaces      # 用户接口层：REST Controller、DTO、Assembler
├── application     # 应用层：应用服务、命令对象、事务编排（不含业务规则）
├── domain          # 领域层：聚合根、实体、值对象、领域事件、Repository 接口、领域服务
└── infrastructure  # 基础设施层：Repository 实现（MyBatis/JPA）、MQ、外部服务适配、配置
```

Dependency direction: `interfaces -> application -> domain <- infrastructure`
（infrastructure 实现 domain 定义的接口，依赖倒置；domain 不反向依赖任何层）

## Layering rules

1. domain 层尽量纯 POJO，不依赖 Spring Web / MyBatis / JPA 注解
2. Repository 接口定义在 domain，实现放在 infrastructure
3. 应用服务只做编排：事务边界、鉴权、调用聚合方法、发布领域事件
4. 业务规则进聚合（充血模型），禁止把核心判断写在 Service 里
5. 值对象不可变，必须重写 equals / hashCode
6. 聚合之间只通过 ID 引用，不持有对方对象引用
7. 跨聚合最终一致性用领域事件 + 事务性 outbox，不做跨聚合事务
8. 简化 CQRS：纯查询场景允许绕过 domain 直接走 infrastructure（禁止用于写路径）
9. 一个聚合一个事务，事务边界在 application service

## Process

### Step 1

识别限界上下文（Bounded Context）与通用语言（Ubiquitous Language），
确定本服务属于哪个上下文。

### Step 2

按上下文划分 Maven / Gradle 模块（单模块分包或父子模块均可，但依赖方向不可违反）。

### Step 3

定义聚合根、实体、值对象，明确每个聚合的不变量（invariants），
不变量必须在聚合构造与状态变更时得到保证。

### Step 4

在 domain 层定义 Repository 接口与领域事件（工厂方法创建聚合优先于公开构造器）。

### Step 5

实现 infrastructure：ORM 映射与领域模型分离（DO/PO 不得穿透到上层）、
事件发布器、外部服务防腐层（ACL）。

### Step 6

编写 application service：每个用例一个方法，`@Transactional` 标注在应用服务层。

### Step 7

实现 interfaces：Controller + DTO + Assembler，DTO 与领域对象双向隔离。

### Step 8

验证：检查依赖方向、domain 纯净度，单测聚焦 domain 层（不启动 Spring 容器）。

## Output

Return results using this structure:

- 模块结构树（module tree）
- 聚合设计说明：聚合边界、不变量、聚合间关系
- 关键类骨架代码（聚合根 / 值对象 / Repository 接口 / 应用服务）
- 违反分层规则的问题清单，按严重度分级：

Critical
High
Medium
Low
Suggestion

## Anti-patterns

- 贫血模型：domain 只有 getter / setter，逻辑全在 Service
- DO / PO 实体从 infrastructure 穿透到 application 或 interfaces
- Controller 直接调用 Repository
- 聚合 A 持有聚合 B 的对象引用（应为 ID）
- 应用服务里堆积 if / else 业务规则
- 为每个表机械地建一个聚合（聚合按不变量划界，不按表）
