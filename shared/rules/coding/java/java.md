# Java Rules

> 适用范围：所有 Java 代码。  
> 边界：本文件只覆盖**语言层面的通用约束**。并发见 `concurrency.md`，异常见 `exception.md`，命名见 `naming.md`，性能见 `performance.md`。  
> 基线版本：Java 17+（record / sealed / switch expression 可用）。

## 0. 核心原则（Core principle）

1. **不可变优先**：默认不可变，需要可变时给出明确理由。
2. **约束在编译期**：能用类型系统拦截的错误，不用运行期检查。
3. **显式优于隐式**：不依赖字段顺序、不依赖反射、不依赖隐式转换。
4. **null 是缺陷信号**：把 null 视为设计问题，而非需要防御的常态。
5. **接口最小化**：类的公开 API 越小，被误用的可能越小。

## 1. 不可变性（Immutability）

- **默认使用不可变对象**：对象创建后状态不再变化。
- **字段能 final 就 final**：包括局部变量、成员变量、静态常量。
- **防御性复制**：构造器与 getter 中，对可变集合/数组做拷贝。
  ```java
  // 错误：外部可绕过封装修改内部状态
  public List<Item> getItems() { return this.items; }

  // 正确：返回不可修改视图或副本
  public List<Item> getItems() { return List.copyOf(this.items); }
  ```
- **禁止暴露可变内部集合**：不用 `Collections.unmodifiableList` 包装原始引用
  （仍可通过原始引用修改），用 `List.copyOf` / `List.of`。
- **不可变对象的判定标准**（全部满足才算）
  - 所有字段 final
  - 类本身 final 或构造器不可被重写影响（可用 sealed / 私有构造）
  - 无 setter，无返回内部可变状态的方法
  - 创建过程中 `this` 未逸出
- **合理例外**：框架强制要求的可变对象（JPA 实体、DTO 绑定、序列化载体），但
  可变范围应最小化（如仅提供受控 setter）。

## 2. 数据载体（Data carriers）

- **优先 record 承载不可变数据**
  - 适用：DTO、值对象、查询结果、方法的复合返回值、事件载荷
  - 不适用：需要可变状态、需要继承、需要大量字段校验逻辑、ORM 实体
- **record 的值语义**：`equals` / `hashCode` 自动按字段生成 —— 不要在其中
  放入可变字段，否则破坏值语义。
- **record 内做紧凑构造器校验**
  ```java
  public record Money(BigDecimal amount, Currency currency) {
      public Money {
          Objects.requireNonNull(amount, "amount");
          Objects.requireNonNull(currency, "currency");
          if (amount.scale() > currency.getDefaultFractionDigits()) {
              throw new IllegalArgumentException("scale exceeds currency precision");
          }
      }
  }
  ```
- **禁止用 record 做 ORM 实体**（需要代理与无参构造）。
- **类与 record 的选择**：行为多、有身份标识 → class；纯数据、只有访问器 → record。

## 3. 依赖注入与装配（Dependency injection）

- **构造器注入优先**
  - 保证依赖不为 null，对象创建即完整
  - 支持 final 字段，天然不可变
  - 便于单元测试直接 new，无需容器
- **禁止字段注入**（`@Autowired` 在字段上）
  - 无法 final、无法在容器外实例化、隐藏依赖数量
- **依赖过多是设计信号**：构造器参数超过 5 个左右，说明职责过重或
  出现了"上帝类"，应拆分而非继续堆注入。
- **不注入容器本身**：禁止注入 `ApplicationContext` 去动态取 Bean，
  这会掩盖依赖关系。
- **setter 注入仅用于**：可选依赖、循环依赖破解（应优先重构消除循环）。
- **第三方无法改构造器的场景**：用 `@Configuration` + `@Bean` 方法显式装配。

## 4. 静态状态（Static state）

- **禁止静态可变状态**
  - 排除：不可变的常量（`static final` 基本类型/String/不可变对象）
  - 禁止：静态可变集合、静态计数器、静态缓存（除非有明确并发安全的实现
    与容量上限，并在注释中说明）
- **静态方法限制**：仅用于纯函数（无副作用、不依赖外部状态）或工厂方法。
- **工具类**：私有构造器 + `final`，或用 Java 17 后直接定义静态方法。
- **单例的正确做法**：交给容器管理（Spring 单例 Bean），而非手写
  `static INSTANCE`。
- **禁止静态代码块做重逻辑**：初始化顺序难以预测，异常难以定位。

## 5. null 与 Optional

- **Optional 只用于返回值**
  - 允许：方法的返回类型，用于显式表达"可能无结果"
  - 禁止：类字段（破坏序列化、不可作为 ORM 属性、增加无意义包装）
  - 禁止：方法参数（应改用重载或重载 + 校验）
  - 禁止：集合元素类型（`List<Optional<T>>` —— 应用过滤代替）
- **Optional 使用规范**
  - 用 `orElse` / `orElseThrow` / `map` / `filter` 组合，不做 `isPresent() + get()` 分支
  - 不要 `Optional.ofNullable` 包装后立刻 `.get()`
  - 不要为"更安全"把所有返回值都包成 Optional —— 只在语义上确实可能无结果时使用
- **公共 API 的 null 契约**
  - 公共方法参数：用 `Objects.requireNonNull` 快速失败
  - 公共方法返回：明确约定是否可能为 null；优先返回空集合而非 null
  ```java
  // 返回空集合，而不是 null
  public List<Order> findOrders(Long userId) {
      return orders.isEmpty() ? List.of() : List.copyOf(orders);
  }
  ```
- **集合返回值禁止为 null**：调用方不应为遍历做 null 判断。
- **合理例外**：`Map.get()` 语义、框架回调要求返回 null、性能敏感的
  紧内循环（须注释说明）。

## 6. 集合与泛型（Collections & generics）

- **接口类型声明，具体类型实现**
  ```java
  List<Order> orders = new ArrayList<>();   // 正确
  ArrayList<Order> orders = new ArrayList<>(); // 错误：暴露实现
  ```
- **返回空集合而非 null**（见 §5）。
- **不可变集合优先**：`List.of` / `Map.of` / `Set.of` / `List.copyOf`。
- **不使用原始类型**：`List` 而非 `List<Object>`；泛型边界用 `extends` / `super`
  遵循 PECS 原则。
- **集合初始容量**：已知规模时指定容量，避免扩容拷贝。
- **禁止在遍历中修改集合**：用迭代器、`removeIf` 或收集后统一处理。

## 7. 类设计与继承（Class design）

- **组合优于继承**：非"是一个"关系一律用组合。
- **为继承设计或禁止继承**：类默认 `final`；确需继承时明确说明扩展点。
- **优先 sealed 限定继承范围**（Java 17+）：
  ```java
  public sealed interface PaymentResult
      permits Success, Failure, Pending {}
  ```
  配合 switch 模式匹配，可用编译期穷尽性检查替代运行期分支。
- **遵循 Liskov**：子类不得强化前置条件、不得弱化后置条件。
- **public 方法越少越好**：默认 private，按需放开。
- **禁止在构造器中调用可重写方法**：子类字段尚未初始化。

## 8. 现代语言特性（Modern Java）

- **switch 表达式优先于语句**：有返回值时用表达式形式。
- **模式匹配简化类型判断**：`instanceof` 后直接绑定变量，不重复强转。
- **text block 用于多行字符串**（SQL、JSON 模板），避免 `+` 拼接。
- **var 的使用边界**：局部变量可用，前提是右侧类型一眼可辨；
  字段、参数、返回值禁止用 var。
- **不使用已废弃 API**：编译告警必须处理，不通过 `@SuppressWarnings` 掩盖。

## 9. 审查清单（Review checklist）

提交 Java 代码前逐项确认：

- [ ] 字段能 final 的都 final 了
- [ ] 没有暴露可变内部状态（集合/数组已复制或返回不可变视图）
- [ ] 依赖通过构造器注入，无字段注入
- [ ] 没有新增静态可变状态
- [ ] Optional 只出现在返回值位置
- [ ] 集合返回值不为 null
- [ ] 数据载体优先用了 record
- [ ] 无原始类型、无未检查转换
- [ ] 新类默认 final，继承点有明确理由
- [ ] 无新增编译告警，无 `@SuppressWarnings` 掩盖
- [ ] 公共方法参数有 null 校验

## 10. 禁止事项（Prohibited）

- 字段注入（`@Autowired` 修饰字段）
- 静态可变集合或静态可变缓存（无并发安全与容量约束）
- Optional 作为字段、参数、集合元素
- 集合类型返回 null
- 返回内部可变集合的直接引用
- 用 record 做 ORM 实体
- 在构造器中调用可重写方法
- 使用原始类型（raw type）
- 未指定容量的批量集合（已知规模时）
- 用 `@SuppressWarnings` 掩盖可修复的告警
