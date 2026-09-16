# Java Naming Rules

> 适用范围：Java 代码的标识符命名。  
> 边界：结构性与不可变性约束见 `java.md`；并发命名（线程、锁、执行器）见`concurrency.md`；异常类的命名与语义见 `exception.md`。  
> 参考基准：Java 语言规范命名约定 + 项目通用语言（见 `architecture/ddd.md`）。

## 0. 核心原则（Core principle）

1. **名字表达意图**：读名字即可知道它是什么、做什么，无需看实现。
2. **名字是契约**：名字暗示的语义必须被实现遵守，不得名实不符。
3. **业务术语优先**：业务概念使用领域语言，不用技术词替代。
4. **长度与作用域成正比**：作用域越大、生命周期越长，名字越完整。
5. **可读性优先于简短**：不为省几个字符牺牲可理解性。

## 1. 通用命名规则（General）

- **禁止拼音与中英混拼**：不用 `getYonghu()`、`userXinxi`。
- **禁止无意义缩写**：除业界通用缩写外（`id`、`url`、`dto`、`api`、`dao`、
  `http`、`config`、`ctx`、`impl`），一律使用完整单词。
  ```java
  int usrCnt;    // 错误
  int userCount; // 正确
  ```
- **禁止序列编号命名**：`handler1`、`handler2`、`temp`、`data2` 一律禁止；
  按职责命名。
- **禁止无业务含义的泛称**：`data`、`info`、`obj`、`temp`、`result`、
  `list`、`map`、`value`（作为类名/字段名时）。
  - 例外：局部临时变量在极小作用域内可宽泛；集合变量应体现元素含义
    （`orders` 而非 `list`）。
- **拼写必须正确**：禁止拼错（`lenght`、`recieve`、`adress`）。
- **统一用词，禁止同义词漂移**：同一概念全项目只用一种叫法。
  禁止 `get` / `fetch` / `query` / `load` 混用表达同一语义。

## 2. 命名风格（Case conventions）

| 元素 | 风格 | 示例 |
|---|---|---|
| 包（package） | 全小写，无下划线 | `com.example.order.domain` |
| 类 / 接口 / 枚举 / 注解 / record | UpperCamelCase | `OrderService`、`Money` |
| 方法 | lowerCamelCase | `calculateTotal` |
| 变量 / 参数 | lowerCamelCase | `orderId`、`pageSize` |
| 常量（`static final`） | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 类型参数（泛型） | 单大写字母或加后缀 | `T`、`E`、`K`、`V`、`R` |
| 枚举常量 | UPPER_SNAKE_CASE | `PENDING`、`PAID` |

- **`static final` 但非编译期常量**（如对象实例、集合）也使用
  UPPER_SNAKE_CASE，与常量保持一致。
- **测试类**：被测类名 + `Test` 后缀（`OrderServiceTest`）。
- **禁止下划线用于普通标识符**（常量除外）；禁止 `_` 或 `$` 开头。

## 3. 布尔命名（Booleans）

- **布尔变量/字段用 `is` / `has` / `can` / `should` 前缀**
  ```java
  boolean isDeleted;    // 正确
  boolean hasPermission;
  boolean canRetry;
  boolean deleted;      // 不推荐：语义不明确
  ```
- **布尔 getter 保留前缀**：`isActive()`、`hasNext()`，
  不使用 `getActive()`（record 的访问器例外，见 §7）。
- **禁止否定式命名**：`isNotReady`、`disableXxx` 会带来双重否定。
  ```java
  boolean isNotValid;   // 错误
  boolean isValid;      // 正确
  ```
- **布尔方法名体现判断**：`isEmpty()`、`isExpired()`，
  不使用 `checkXxx()`（无法从名字判断返回什么）。

## 4. 方法命名（Methods）

- **动词开头，动宾结构**：`saveOrder`、`calculatePrice`、`validateInput`。
- **查询语义按返回类型区分**

  | 场景 | 用词 | 说明 |
  |---|---|---|
  | 按标识精确查找 | `get` | 约定必然存在，找不到应抛异常 |
  | 可能不存在 | `find` / `findXxxOrNull` | 返回 `Optional` 或 null |
  | 查询集合 | `list` / `findAll` | 返回集合，可能为空集合 |
  | 存在性判断 | `exists` | 返回 boolean |
  | 计数 | `count` | 返回数值 |

- **`get` 与 `find` 不可混用**：这是可检验的接口契约，混用会让调用方
  无法判断"查不到"是异常还是空值。
- **修改语义区分**

  | 场景 | 用词 |
  |---|---|
  | 新增 | `create` / `add` / `insert` |
  | 更新 | `update` / `modify` |
  | 删除 | `delete` / `remove` |
  | 保存（新增或更新） | `save` |

- **`add` 与 `set` 区分**：`addItem` 追加，`setItems` 整体替换。
- **转换方法命名体现方向**
  - `toXxx()` —— 转换为另一种类型，产生新对象（`toEntity()`、`toDto()`）
  - `fromXxx()` —— 静态工厂，从某类型构建（`Money.from(BigDecimal)`）
  - `asXxx()` —— 视图/包装，不改变本质
- **回调与钩子用过去式或 `on` 前缀**：`onSuccess`、`created`。
- **禁止 `process` / `handle` / `doXxx` / `execute` 这类空泛动词**，
  除非确实无法更具体（且应质疑其设计）。

## 5. 类命名（Classes）

- **禁止无信息量后缀**：`Manager`、`Helper`、`Util`、`Utils`、`Processor`、
  `Handler`（作为业务类名时）、`Common`、`Base`、`Abstract`。
  这类名字说明职责未被定义清楚。
  - 合理的替代：按实际职责命名 —— `OrderPricing`、`InvoiceCalculator`
  - 例外：`*Utils` 仅用于无状态、纯粹的工具方法集合，且确实跨多个领域复用
- **实现类与接口**
  - 接口不加 `I` 前缀（`OrderRepository` 而非 `IOrderRepository`）
  - 实现类加 `Impl` 仅用于单一实现且无更好命名时；
    有明确技术特征的实现用特征命名（`JpaOrderRepository`、`RedisCacheStore`）
- **抽象类**用 `Abstract` 前缀（`AbstractEventHandler`）。
- **异常类**以 `Exception` 结尾（见 `exception.md`）。
- **测试类**：`<被测类>Test`；集成测试 `<被测类>IT` 或 `...IntegrationTest`。
- **DTO 按用途命名**：`CreateOrderRequest`、`OrderDetailResponse`、
  `OrderSummary`，禁止 `OrderDTO` 这种无区分度的名字。
- **枚举用单数**：`OrderStatus` 而非 `OrderStatuses`。

## 6. 包命名（Packages）

- 全小写，不用下划线，不用复数形式。
- 遵循项目既有分层/分模块结构，不新增平行结构。
- 包名体现职责而非技术实现细节（`order.pricing` 优于 `order.util`）。
- 禁止包级别的"杂物间"（`common`、`misc`、`utils` 无边界膨胀）。

## 7. DDD 与领域命名（Domain naming）

> 完整规则见 `architecture/ddd.md`，此处只列命名相关约束。

- **使用通用语言**：类名/方法名使用业务术语，与技术术语分离。
  ```java
  // 错误：技术词命名业务概念
  String statusFlag;  boolean deletedFlag;
  // 正确
  OrderStatus status;  boolean isCancelled;
  ```
- **领域事件用过去式**：`OrderCreated`、`PaymentFailed`。
- **值对象用名词**：`Money`、`EmailAddress`、`DateRange`。
- **聚合根用领域名词**：`Order`、`Invoice`，不加 `Aggregate` / `Root` 后缀。
- **领域服务用业务动作**：`PricingPolicy`、`TransferService`，
  禁止 `XxxManager`。
- **record 访问器不带 `get` 前缀**：`order.id()` 而非 `order.getId()`
  （语言特性约定，与 JavaBean 风格有意区分）。
- **方法命名表达业务意图**，不暴露实现步骤：
  ```java
  order.cancel();              // 正确
  order.setStatus(CANCELLED);  // 错误：暴露内部状态机
  ```

## 8. 一致性（Consistency）

- **同层同类同名**：同类职责在不同模块中命名方式一致
  （都用 `XxxService`，不混用 `XxxBiz`）。
- **遵守既有约定**：项目已有命名风格优先于个人偏好；
  即使既有风格不理想，也不在局部引入新风格。
- **成对命名对应**：`open`/`close`、`start`/`stop`、`create`/`destroy`、
  `acquire`/`release`、`lock`/`unlock`、`add`/`remove`。
  禁止 `open`/`destroy` 这类不成对的组合。
- **改名前先检索引用**：全仓库确认引用方可改，改名必须一次性完整替换。
- **禁止为"打字方便"创造的别名**：`seq`、`no`、`idx` 应写为
  `sequence`、`number`、`index`（业界通用缩写除外）。

## 9. 审查清单（Review checklist）

- [ ] 无拼音、无中英混拼
- [ ] 无无意义缩写（仅使用业界通用缩写）
- [ ] 无序列编号命名（xxx1/xxx2/temp/data2）
- [ ] 无 `data`/`info`/`obj` 等无业务含义名
- [ ] 拼写正确，无同义词漂移
- [ ] 命名风格符合元素类型（类/方法/常量/枚举）
- [ ] 布尔命名使用 is/has/can/should，且无否定式
- [ ] `get` 与 `find` 语义按契约区分
- [ ] 转换方法使用 to/from/as 并方向正确
- [ ] 无 `Manager`/`Helper`/`Process` 等无信息量命名
- [ ] 接口无 `I` 前缀，实现命名体现技术特征
- [ ] DTO 按用途命名，且有区分度
- [ ] 领域命名使用通用语言，事件用过去式
- [ ] 成对操作命名对应（open/close、add/remove）
- [ ] 改动范围内的命名风格与既有代码一致

## 10. 禁止事项（Prohibited）

- 拼音命名或中英混拼（`getYonghu`、`userXinxi`）
- 无意义缩写（`usrCnt`、`addrTmp`）
- 序列编号命名（`handler1`、`temp2`、`data3`）
- 无业务含义的泛称作为类名或字段（`data`、`info`、`obj`）
- 拼写错误
- `Manager` / `Helper` / `Processor` / `Common` / `Base` 作为业务类名
- 接口加 `I` 前缀
- 否定式布尔命名（`isNotReady`、`isDisable`）
- 布尔 getter 使用 `get` 前缀（record 除外）
- `get` 与 `find` 混用表达同一语义
- 空泛动词命名（`process`、`handle`、`doSomething`、`execute`）
- 同一概念使用多个同义词（`get`/`fetch`/`query` 混用）
- 成对操作命名不成对（`open` / `destroy`）
- 局部引入与既有代码不一致的命名风格
- 下划线或 `$` 开头命名标识符
