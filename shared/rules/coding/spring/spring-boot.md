# Spring Boot Rules

> 适用范围：Spring Boot 应用的分层、装配、Web 层与配置。  
> 边界：依赖注入细节见 `dependency-injection.md`，事务见 `transaction.md`，配置绑定细节见 `configuration.md`，参数校验见 `validation.md`。  
> 基线版本：Spring Boot 3.x（Jakarta EE 命名空间）。

## 0. 核心原则（Core principle）

1. **分层是契约，不是建议**：每层职责单一，禁止跨层直连。
2. **框架负责装配，不负责业务**：业务规则必须在可独立测试的普通类里。
3. **默认按需暴露**：能不给外部的能力就不给（端点、Bean、配置项）。
4. **启动即失败**：配置错误、依赖缺失应在启动时暴露，不留到运行时。
5. **约定优于配置，但显式优于隐式**：非默认行为必须能被一眼看到。

## 1. 分层与职责（Layering）

标准分层与允许的调用方向：

```
Controller  ->  Service  ->  Repository  ->  DB
     |             |
    DTO         Domain
```

- **Controller（Web 层）**
  - 只做：协议转换（HTTP ↔ 领域/应用对象）、参数绑定、校验触发、状态码映射
  - **禁止包含业务逻辑**：不写 if/else 业务判断、不编排多个 Repository、
    不做计算与聚合
  - **禁止直接调用 Repository**（除极简只读查询且经明确豁免）
  - 方法体通常应能压缩到 5 行以内；超长说明逻辑放错了层

- **Service（应用/领域层）**
  - 承担业务规则、用例编排、事务边界
  - 不感知 Web 概念：不接收 `HttpServletRequest`、不返回 `ResponseEntity`

- **Repository（持久层）**
  - 只做数据访问，不写业务判断
  - 不向上层泄露 ORM 特有类型（`EntityManager`、`Criteria`、`Session`）

- **禁止跨层直连**：Controller 跳 Service 调 Repository、Service 调 Controller
  等反向依赖一律禁止。

## 2. 依赖管理与注入（Wiring）

- **构造器注入**：默认方式，保证依赖完整、字段可 final、便于测试。
- 详细规则与反例见 `dependency-injection.md`，本文件不重复展开。
- **Bean 作用域**
  - 默认单例：Bean 必须**无状态**或状态线程安全
  - 禁止在单例 Bean 中持有请求级可变状态（用户、租户、请求上下文）
    → 用方法参数或 `RequestContextHolder` 等显式传递
- **Bean 数量控制**：单一 `@Configuration` 类中 `@Bean` 方法过多时考虑拆分。
- **装配失败要显式**：优先构造器注入让缺失依赖在启动期报错，而不是
  运行期 `NullPointerException`。

## 3. Web 层与 API（Controllers & API）

- **禁止直接暴露持久化实体**
  - 入参用请求 DTO，出参用响应 DTO
  - 原因：实体含懒加载代理、内部字段、循环引用、ORM 注解；
    直接暴露会导致序列化异常、字段泄露、契约与表结构强耦合
  ```java
  // 错误
  @GetMapping("/{id}")
  public UserEntity get(@PathVariable Long id) { ... }

  // 正确
  @GetMapping("/{id}")
  public UserResponse get(@PathVariable Long id) { ... }
  ```
- **DTO 与实体分离的转换**：在明确的边界处转换（Controller 内或专用
  Assembler / Mapper），禁止在 Service 内部来回转换。
- **HTTP 语义正确**
  - `GET` 只读且幂等；`POST` 创建；`PUT` 全量替换；`PATCH` 局部更新；`DELETE` 删除
  - 禁止用 `GET` 执行有副作用的操作
  - 状态码：创建返回 201 + Location；无内容返回 204；参数错误 400；
    未认证 401；无权限 403；资源不存在 404；冲突 409
- **统一响应结构**：错误响应格式全应用一致，由全局异常处理器产出，
  禁止每个 Controller 各自拼装。
- **全局异常处理**：用 `@RestControllerAdvice` 集中处理，禁止在 Controller 里
  写大段 try-catch 转错误码。
- **接口版本与兼容**：对外接口变更遵循 `common/general.md` 的兼容性优先级。
- **分页**：所有列表接口必须分页，并设定最大页大小上限，防止全表拉取。
- **参数校验**：在 DTO 上用注解声明约束并触发校验，细节见 `validation.md`。

## 4. 配置管理（Configuration）

- **`@ConfigurationProperties` 优先于分散的 `@Value`**
  - 相关配置聚合成一个带前缀的对象，便于校验、复用、IDE 提示
  - 禁止在业务代码里散落 `@Value("${...}")` 取同一组配置
- **配置对象必须校验**：`@Validated` + JSR-303 注解，非法配置启动即失败。
  ```java
  @ConfigurationProperties(prefix = "app.order")
  @Validated
  public record OrderProperties(
      @NotNull Duration timeout,
      @Min(1) @Max(1000) int batchSize) {}
  ```
- **优先级明确**：命令行 > 环境变量 > 环境配置 > 默认配置。
  密钥类配置**禁止写入代码仓库或打包进制品**，只从环境变量/密钥服务获取。
- **禁止硬编码环境差异**：地址、端口、开关必须外置为配置。
- **配置项有默认值且有文档**：新增配置项须在示例配置中体现。

## 5. 应用启动与生命周期（Startup）

- **启动即校验**：外部依赖、关键配置、必要资源在启动阶段检查并快速失败。
- **禁止在 `@PostConstruct` 中做重逻辑或远程调用**
  - 阻塞启动、失败难定位、可能与容器初始化顺序竞争
  - 需要预热或后台任务时用 `ApplicationRunner` 或显式调度
- **优雅停机**：启用优雅停机，确保在途请求完成、资源正常释放。
- **健康检查**：暴露健康端点，区分存活（liveness）与就绪（readiness）。
- **启动日志**：关键配置摘要（脱敏后）在启动时打印一次，便于排查。

## 6. 日志与可观测性（Observability）

- **使用 SLF4J 门面**，禁止直接使用 `System.out` / `e.printStackTrace()`。
- **参数化日志**：用占位符而非字符串拼接，避免无谓的对象构造。
  ```java
  log.info("order created, id={}, userId={}", orderId, userId);  // 正确
  log.info("order created, id=" + orderId);                      // 错误
  ```
- **级别使用符合 `common/general.md`**：ERROR 需人介入，WARN 需关注。
- **异常日志记录完整堆栈**，且不重复记录（同一异常在多层各打一次）。
- **补充指标与链路**：关键路径增加指标埋点；跨服务调用透传追踪标识。

## 7. 测试（Testing）

- **分层测试策略**
  - 领域/业务逻辑：纯单元测试，不启动容器
  - Controller：`@WebMvcTest` 切片测试（仅 Web 层）
  - Repository：`@DataJpaTest` / Testcontainers
  - 端到端：`@SpringBootTest`，少量且聚焦关键链路
- **禁止全部使用 `@SpringBootTest`**：全量上下文启动慢，且掩盖分层问题。
- **测试不得依赖执行顺序**、不得依赖生产数据。
- **外部依赖在测试中隔离**：数据库、消息、第三方调用须可替换（Testcontainers、
  Mock、Stub）。
- **测试随代码提交**：新增行为与缺陷修复必须附带测试。

## 8. 启动性能与依赖（Startup performance）

- **控制组件扫描范围**：避免全包扫描，缩小 `@ComponentScan` 边界。
- **按需引入 Starter**：不用的自动配置依赖及时移除，或用
  `spring.autoconfigure.exclude` 排除。
- **懒加载谨慎使用**：仅用于确实非必需、初始化昂贵的 Bean，
  并注明原因（它会推迟失败、增加首次请求延迟）。
- **定期检查启动耗时**：关注启动时间变化，异常增长通常是依赖膨胀的信号。

## 9. 安全（Security）

- **默认拒绝**：新增接口默认需要鉴权，放行需显式声明。
- **不泄露内部信息**：生产环境关闭堆栈详情、关闭不必要的管理端点。
- **敏感端点保护**：Actuator 管理端点须鉴权或仅内网可达。
- **输入不可信**：所有外部输入做校验，含内部服务间调用。
- **越权防护**：资源访问须校验归属关系，不能只依赖前端传递的 ID。
- **CORS / CSRF**：按需最小化放开，禁止 `*` 通配到生产环境。

## 10. 审查清单（Review checklist）

提交 Spring Boot 代码前逐项确认：

- [ ] Controller 内无业务逻辑、无 Repository 直连
- [ ] 未直接暴露持久化实体，入参出参均为 DTO
- [ ] HTTP 方法与状态码语义正确
- [ ] 错误响应由全局异常处理器统一产出
- [ ] 列表接口已分页且有最大页大小限制
- [ ] 依赖通过构造器注入（详见 `dependency-injection.md`）
- [ ] 单例 Bean 无请求级可变状态
- [ ] 配置使用 `@ConfigurationProperties` 且有校验
- [ ] 无硬编码环境信息，密钥未入库
- [ ] `@PostConstruct` 中无重逻辑与远程调用
- [ ] 日志使用 SLF4J + 占位符，无敏感信息
- [ ] 新接口默认需要鉴权
- [ ] 测试为切片测试，非全量 `@SpringBootTest`
- [ ] 新增配置项已更新示例配置

## 11. 禁止事项（Prohibited）

- Controller 中包含业务逻辑或业务分支判断
- Controller 直接调用 Repository（无明确豁免）
- 直接通过 REST 暴露持久化实体
- 用 `GET` 执行有副作用的操作
- 列表接口无分页或无页大小上限
- 手工拼接错误响应，未走统一异常处理
- 使用字段注入（见 `dependency-injection.md`）
- 单例 Bean 中保存请求级可变状态
- 在业务代码中散落 `@Value` 取同一组配置
- 密钥、连接串硬编码或提交到版本库
- `@PostConstruct` 中做远程调用或重逻辑
- 使用 `System.out` / `printStackTrace()`
- 生产环境暴露完整堆栈信息
- 测试全部依赖 `@SpringBootTest`
