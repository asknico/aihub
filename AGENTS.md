# AIHub — Agent 操作契约（Agent Operating Contract）

> **读者：** 在本仓库内运行的所有 AI Agent。
> **范围：** 仅限 AIHub 控制面（Control Plane）。业务项目的约定属于各项目自己的 `AGENTS.md`。
> **原则：** 规则必须是确定性的、可测试的、可执行的。含糊的指导不是规则。
> 本文件中「必须 / 禁止 / 可以 / 应当」遵循 RFC 2119 语义。
>
> **状态图例**
> ✅ 已落地 —— 路径存在且可用
> ⬜ 规划中 —— 路径不存在或为空，**禁止当作已生效引用**
>
> 完整清单见 §20。引用任何目标前先核对该节。

---

## 0. 使命（Mission）

AIHub 是**可共享、可版本化管理的 AI Agent 配置资产**的唯一权威来源。

AIHub **可以**管理：

- Agent 适配器（Agent Adapter）
- 规则（Rules）
- 技能（Skills）
- 角色档（Profiles）
- 提示词（Prompts）
- MCP 定义
- 可复用知识（Knowledge）
- 模板（Templates）
- 注册表（Registries）

AIHub **不**拥有：

- 密钥（Secrets）
- 凭据（Credentials）
- Agent 会话（Sessions）
- 运行时状态（Runtime state）
- 本机状态（Local machine state）
- 个人记忆（Memory）
- 临时文件（Temporary files）
- 业务项目源代码

以上内容属于 Git 仓库之外、`AIHUB_DATA` 指向的位置。

---

## 1. 仓库边界（Repository Boundaries）

### AIHub

`AIHUB_HOME` 指向这个 Git 仓库。只有**确定性的、可共享的、可版本化的资产**才属于这里。

```text
AIHub/                    # 以下均为实际存在的顶层目录
├── .githooks/            # ✅ pre-commit 钩子
├── .github/              # ✅ CI 工作流 / CODEOWNERS / dependabot
├── .vscode/              # ✅ 编辑器配置示例
├── agents/               # ✅ 各 Agent 适配器
├── config/               # ✅ Hub 级配置
├── docs/                 # ✅ 文档
├── mcp/                  # ✅ MCP 定义
├── profiles/             # ✅ 角色档
├── registry/             # ✅ 注册表（生成物）
├── runtime/              # ✅ 本机运行时（不入库）
├── scripts/              # ✅ 工具脚本
├── shared/               # ✅ 共享事实源
└── templates/            # ⬜ 目录为空，脚手架模板尚未落地
```

### AIHUB_DATA

`AIHUB_DATA` 指向**仓库之外**的本地私有数据。它与 `AIHUB_HOME` 是两条独立路径，无法互相推导，因此必须由环境变量单独定义。

```text
${AIHUB_DATA}/
├── local/          # ⬜ 本地覆盖
├── secrets/        # ⬜ 密钥
├── memory/         # ⬜ 本机记忆
├── sessions/       # ⬜ 会话
├── state/          # ⬜ 运行时状态
├── cache/          # ⬜ 缓存
├── logs/           # ⬜ 日志
└── tmp/            # ⬜ 临时文件
```

`AIHUB_DATA` **禁止**提交到 Git。

⚠️ **已知不一致**：`.env` 中 `AIHUB_DATA` 的字面值与磁盘上的实际目录名对不上，见 §20「已知不一致」。

---

## 2. 单一事实源规则（Source-of-Truth Rules）

每个概念有且只有一个权威来源。

| 概念 | 权威来源 | 落地 |
|---|---|---|
| Hub 级策略 | `AGENTS.md`（本文件） | ✅ |
| 全局规则 | `shared/rules/**` | ✅ |
| 技能 | `shared/skills/**` | ✅ |
| 知识 | `shared/knowledge/**` | ⬜ 空 |
| 提示词 | `shared/prompts/**` | ⬜ 空 |
| 角色档 | `profiles/**` | ✅ |
| Agent 适配器 | `agents/<agent-id>/**` | ✅ |
| MCP 定义 | `mcp/**` | ✅ |
| 模板 | `templates/**` | ⬜ 空 |
| 注册表 | `registry/**` | ✅ |
| 团队级结论 | `shared/memory/**` | ⬜ 空（入库） |
| 本地覆盖 | `${AIHUB_DATA}/local/**` | ⬜ |
| 密钥 | `${AIHUB_DATA}/secrets/**` | ⬜ |
| 本机记忆 | `${AIHUB_DATA}/memory/**` | ⬜ |
| 运行时状态 | `${AIHUB_DATA}/state/**` | ⬜ |

**禁止**在多个位置手工维护同一份信息。优先用引用，而不是复制。

**「记忆」的两个平面不得混用：**

- 跨会话有效、团队可共享、需要版本化的结论 → `shared/memory/`（**入库**）
- 本机私有、随时可丢的会话记忆 → `${AIHUB_DATA}/memory/`（**不入库**）

---

## 3. Hub 与项目的职责划分（Hub vs Project Responsibility）

AIHub 定义：**Agent 应当如何工作。**
业务仓库定义：**项目是什么、适用哪些项目级约束。**

业务项目的 `AGENTS.md` **可以**引用 AIHub 的规则与技能。**禁止**把共享规则复制进项目 —— 除非项目有意分叉（fork）该规则。

属于**项目级**的例子：

- 限界上下文（Bounded Context）
- 聚合（Aggregate）
- 业务不变量（Invariant）
- 项目架构
- API 约定
- 项目依赖
- 数据库约束
- 项目专属安全要求

属于**全局**的例子：

- Java 约定
- Spring Boot 约定
- DDD 方法论
- 安全编码
- Git 约定
- Agent 行为
- 代码评审流程

---

## 4. 资产分类（Asset Classification）

创建文件之前，先分类。

| 内容 | 判据 | 去处 | 落地 |
|---|---|---|---|
| 强制约束 | 任何任务都必须遵守、可判定 | `shared/rules/<domain>/` | ✅ |
| 可复用任务流程 | 仅某类任务触发、有明确步骤 | `shared/skills/<domain>/<skill>/` | ✅ |
| 稳定可复用知识 | 稳定成立的事实、决策、术语 | `shared/knowledge/<domain>/` | ⬜ |
| 可复用提示词 | 可复用的 prompt 片段 | `shared/prompts/<domain>/` | ⬜ |
| 角色 / 能力组合 | 某角色适用哪些能力 | `profiles/` | ✅ |
| Agent 专属适配 | 映射到具体 Agent 的原生配置 | `agents/<agent-id>/` | ✅ |
| MCP 声明 | MCP 服务器与 profile | `mcp/` | ✅ |
| 可复用脚手架 | 项目 / 文件模板 | `templates/` | ⬜ |
| 团队级结论 | 跨会话有效的团队沉淀 | `shared/memory/` | ⬜ |
| 本地覆盖 | 仅本机生效 | `${AIHUB_DATA}/local/` | ⬜ |
| 密钥 | 任何密钥材料 | `${AIHUB_DATA}/secrets/` | ⬜ |
| 本机记忆 | 私有、随时可丢 | `${AIHUB_DATA}/memory/` | ⬜ |
| 运行时状态 | 本机私有 | `${AIHUB_DATA}/state/` | ⬜ |
| 缓存 / 临时 / 日志 | 可随时丢弃 | `${AIHUB_DATA}/{cache,tmp,logs}/` | ⬜ |
| 运行状态（仓库内） | 装配产物、本机私有 | `runtime/` | ✅ |

**反向判据**（对不上号就不要放）：

- 能从代码里读出来的事实（表结构、接口签名）→ 不进 knowledge
- 待办与进度 → 不进 knowledge，进 memory
- 密钥 → 不进以上任何位置

如果内容不适合任何一类，先弄清归属再创建。

---

## 5. 强制操作规则（Mandatory Operating Rules）

### 改动前

1. **先读后动**：先读本文件，再读 `shared/rules/common/general.md`（L0），然后按 `read-when` 命中本次任务的相关规则。
2. **确定场景**：确定任务类别与适用的 Profile。
3. **按需加载**：只加载与任务相关的规则和技能，禁止预加载整库（§6）。
4. **先检索后创建**：创建新文件前先查看既有文件，检索是否已有等价规则或技能；发现内容重复，先合并再继续。

### 改动中

5. **最小且内聚**：做最小连贯改动；一次提交只做一件事，禁止把重构、格式化与功能变更混在同一批改动里（保证可回滚）。
6. **先看引用方**：修改共享资产前，先确定受影响的引用方（Profile / registry / Agent 适配器）。
7. **元数据单一来源**：规则与技能的元数据以文件内 frontmatter 为准；`registry/*.yaml` 是生成物，禁止手工编辑（§8、§11）。
8. **守住体量上限**：单文件上限与 frontmatter 要求见 §8；超出部分拆到同级 `references/`。

### 完成后

9. **先验证后报告**：结果未经验证不得宣称完成；校验工具缺失或不完整时，必须如实说明该局限（§15）。
10. **留下记录**：每次实质性工作追加一行到 `shared/memory/YYYY-MM-DD.md`（只追加，不回写历史）。

### 红线（任何时候）

- **密钥隔离**：真实密钥只放仓库根目录 `.env`（不入版本库）；`.env.example` 只允许出现键名与占位符。
- **运行时隔离**：临时文件、缓存、日志只写 `runtime/`；除此之外禁止在仓库内产生任何生成物。
- **不确定就问**：一次确认的成本远低于一次错误变更；禁止基于猜测修改共享层。

当所需信息缺失或互相矛盾时，停止受影响的变更，并报告该歧义。

---

## 6. 规则加载模型与预算（Rule Loading Model）

规则采用渐进披露（Progressive Disclosure），**加载总量必须受控**。

| 层 | 内容 | 加载方式 | 预算 | 落地 |
|---|---|---|---|---|
| 入口 | 本文件 | 每次会话全文注入 | ≤700 行 / 20KB | ✅ |
| L0 常驻 | `shared/rules/common/general.md` 核心原则 | 每次会话注入 | ≤10KB | ✅ |
| L1 场景 | `profiles/<角色>.yaml` 圈定的 5-8 条规则 | 会话开始注入 | ≤48KB | ✅ |
| L2 任务 | 按任务意图 / 文件类型 / 技术栈 / `read-when` 命中的额外规则 | 命中才读 | 不占常驻预算 | ✅ |
| L3 引用 | `references/`、`shared/knowledge/**` | 明确需要时才读 | 不占常驻预算 | ⬜ 知识层为空 |
| 技能 | `profiles/<角色>.yaml` 圈定的技能 | 仅注入 frontmatter 的 `description`，正文命中才读 | 不占常驻预算 | ✅ |

**预算计法**：L0 与 L1 各自独立统计 —— 角色档里列出 `common/general.md` 只为显式声明依赖，该文件只计入 L0，不重复计入 L1。技能走渐进披露，其体积不计入常驻预算。

**禁止**预加载整个规则库、技能库或知识库。

**优先级链**（冲突时从高到低）：

```text
用户显式指令 > common/general.md > 领域规则（coding|architecture|...） > 技能内约束
```

发现规则冲突时：按高优先级执行，**并在回复中指出冲突位置**，不得静默取舍。

---

## 7. 配置解析与优先级（Resolution and Precedence）

生效配置由以下部分解析合成：

```text
Hub（本契约）
  + Profile（角色档）
  + Agent Adapter（Agent 适配器）
  + Project（项目级约定）
  + Local Override（本地覆盖）
```

一般优先级（从高到低）：

```text
项目级指令 > Profile > 全局规则 > Skill 指引
```

但标记为以下属性的规则例外：

```yaml
priority: critical
overridable: false
```

此类规则**禁止**被以下任何一方削弱：Profile、项目、Skill、Agent 适配器、本地覆盖。

典型的不可覆盖规则：密钥保护、凭据处理、破坏性操作防护、仓库安全约束。

⬜ 当前 6 个已写好的规则文件**均无 frontmatter**（§8），因此上述例外机制尚未生效 —— 裁决退回 §6 的优先级链。

当两条适用规则冲突时：

1. 指出这两条规则。
2. 按优先级裁决。
3. 报告该冲突。
4. **禁止**静默忽略高优先级规则。

---

## 8. 规则契约（Rule Contract）

每条规则**必须**包含 frontmatter：

```yaml
id:
title:
scope:
category:
priority:
load:
read-when:
updated:
```

推荐补充字段：`version:` `tags:` `overridable:` `applies-to:`

**体量上限**（按实测校准，超出部分拆到同级 `references/`）：

| 对象 | 上限 |
|---|---|
| 单条规则文件 | ≤250 行 / 12KB |
| 技能 `SKILL.md` | ≤300 行 |
| 本文件（`AGENTS.md`） | ≤700 行 / 24KB |

规则**必须**：描述可执行的约束；避免主观措辞；只包含一个内聚的关注点；不与其他规则重复；用引用关联相关规则，而不是复制。

优先使用小而可组合的规则，而不是大而全的规则文件。

⬜ 当前 `shared/rules/` 共 70 个文件，仅 6 个已写好，且**都还没有 frontmatter** —— 见 §20。

---

## 9. 技能契约（Skill Contract）

Skill 表示一个可复用的工作流，不是常驻规则。

标准结构：

```text
skill-name/
├── SKILL.md          # 必需
├── references/
├── examples/
├── templates/
├── scripts/
└── tests/
    └── cases.yaml
```

只创建该技能真正会用到的目录。

`SKILL.md` **必须**描述：何时适用该技能；所需输入；执行流程；预期输出；验证标准；必需的 references；相关时的权限或工具。

`references/` 里每个文件**必须**在 `SKILL.md` 正文注明「何时读」。frontmatter 的 `description` 写**触发条件**（中英双写），不写功能介绍。

详细知识放 `references/`，不要堆进一个过大的 `SKILL.md`。

---

## 10. Agent 适配器契约（Agent Adapter Contract）

`agents/<agent-id>/` 的存在只有一个目的：把 AIHub 的权威资产适配到某个 Agent 的原生配置模型。

Agent 目录**禁止**变成以下内容的独立来源：共享规则、共享技能、共享知识、密钥、运行时状态。

**已登记 Agent**（唯一登记处：`registry/agents.yaml`）：

| id | 路径 | `skillMode` |
|---|---|---|
| `claude` | `agents/claude/` | `symlink` |
| `codex` | `agents/codex/` | `symlink` |
| `cursor` | `agents/cursor/` | 未声明 |
| `deepseek` | `agents/deepseek/` | 未声明 |

标识全仓统一用上表四个 key；新增 Agent 必须先登记再建目录。

一个 Agent 适配器**可以**包含：

```text
agents/<id>/
├── AGENTS.md / CLAUDE.md   # 入口指引：只引用本文件，禁止复制其条款
├── config.yaml             # 私有配置：只写与 agent-defaults 的差异项
├── mappings.yaml           # 路径映射：源 → 目标，不做内容复制
├── skills/                 # 指向 shared/skills 的目录联接（生成物）
└── projects/               # ⬜ 产出物落盘位置
```

公共默认值集中在 `agents/_shared/agent-defaults.yaml`，各 Agent 只写差异项。

**优先使用链接、渲染或引用权威资产，而不是复制。**

`skills/` 联接由 `scripts/install.py` 装配，是**生成物**：禁止在其中新增、修改或删除文件 —— 改动会同时影响其他 Agent，也绕过 §13 的变更流程。联接不入版本库（见 `.gitignore`），换机器后重跑安装脚本即可。

---

## 11. 注册表契约（Registry Contract）

`registry/**` 是生成态（generated state）。**禁止**手工编辑 registry 文件。

权威元数据与其所属的源资产放在一起。

Registry 生成流程：

```text
源资产（Source Assets）
   ↓
校验（Validation）
   ↓
扫描器（Scanner）
   ↓
生成 Registry
   ↓
一致性检查（Consistency Check）
```

使用仓库自带的同步工具重新生成 registry。生成的 registry 内容**必须**可以从权威源完整复现。

⬜ `scripts/sync.py` 当前为 0 字节；现有 `registry/*.yaml` 是早期手工产物，与实际状态不符 —— 见 §20。

---

## 12. 安全边界（Security Boundary）

**禁止**提交：

- API Key
- 访问令牌（Access Token）
- 刷新令牌（Refresh Token）
- 密码
- Cookie
- 会话数据
- 私钥（Private Key）
- 凭据
- 生产环境密钥
- 敏感内网端点

配置文件**必须间接**引用密钥。推荐写法：

```yaml
api_key_env: OPENAI_API_KEY
```

**禁止**：

```yaml
api_key: 真实密钥值
```

`.env.example` 只定义变量名和安全占位符（它是唯一键名清单，新增变量必须同步登记）。真实密钥存放于配置好的外部密钥机制或 `${AIHUB_DATA}/secrets/`。

**私有 Git 仓库不是密钥保险箱。**

---

## 13. 变更安全（Change Safety）

每一次变更必须：范围明确（scoped）；可评审（reviewable）；可复现（reproducible）；可回滚（reversible）。

**禁止**把以下不相关内容混在一起：重构、格式化、配置变更、行为变更、生成文件变更。

重命名、移动或删除共享资产之前：

1. 检索所有引用。
2. 找出受影响的 Profile。
3. 找出受影响的 Agent 适配器。
4. 找出受影响的 registry。
5. 找出受影响的模板。
6. 原子化地更新所有依赖方。
7. 重新生成生成态。
8. 验证引用。

---

## 14. 生成文件（Generated Files）

被明确标记为 generated 的文件**禁止**手工编辑，含 `registry/**`、`AIHUB_STRUCTURE.md`、`AIHUB_TREE.txt`、`agents/<id>/skills/` 联接。

生成物**必须**能说明：它的来源；它的生成器；如何重新生成它。

如果生成输出与源状态意外不一致，**修复源或生成器，而不是修补生成输出**。

---

## 15. 校验（Validation）

适用的校验通过之前，变更不算完成。

校验应当覆盖：

```text
结构 → 元数据 → 引用 → Profile → Registry → 安全 → Agent 映射
```

工具存在时，优先使用：

```powershell
scripts/install.py --check-only   # ✅ 目录骨架 / 配置键名 / 角色档 / 技能联接
scripts/fix-eol.py                # ✅ 换行符策略体检（只读；--write 才改写）
scripts/validate.py               # ⬜ 0 字节，未实现
scripts/security-check.py         # ⬜ 0 字节，未实现
scripts/sync.py                   # ⬜ 0 字节，未实现
scripts/doctor.py                 # ⬜ 0 字节，未实现
```

**禁止**在所需工具缺失、不完整或未实际执行的情况下，宣称校验已通过。必须明确报告该局限。

---

## 16. Git 安全（Git Safety）

提交之前：确认没有密钥被暂存；确认生成的 registry 已同步；确认引用可解析；审查 diff；排除无关修改。

**禁止**执行破坏性 Git 操作，除非获得明确授权。**禁止**覆盖用户的无关改动。

一次提交应当代表一个内聚的意图。

**钩子**：`.githooks/pre-commit` 检查换行符策略与密钥文件名。`core.hooksPath` 存在 `.git/config` 里，**不随克隆分发** —— 换机器或重新克隆后**必须**重设：

```sh
git config core.hooksPath .githooks
```

---

## 17. 项目生成（Project Generation）

AIHub 模板可以生成业务项目，但生成的项目**不归** AIHub 仓库所有。

项目默认输出位置在 `AIHUB_HOME` 之外，例如：

```text
C:\Work\
├── AIHub\            # 控制面
├── AIHub_Data\       # 数据面（本地私有，不入库）
└── Projects\         # ⬜ 生成的项目，尚未落地
    ├── order-service\
    └── payment-service\
```

生成的项目应当包含自己的 `AGENTS.md`、`.agents/`、`docs/`。项目级规则与知识留在项目里。

可复用的改进应当**有意识地**反哺回 AIHub，**禁止**自动回流。

---

## 18. 完成定义（Definition of Done）

宣布 AIHub 任务完成之前，逐项核对：

- [ ] 归属与目录正确
- [ ] 没有重复的权威信息
- [ ] 必需元数据齐全
- [ ] 引用有效（目标存在且非空）
- [ ] 适用的 Profile 仍然有效
- [ ] Agent 映射仍然有效
- [ ] 需要时已重新生成 Registry
- [ ] 未引入密钥
- [ ] 未改动无关文件
- [ ] 工具可用处已执行校验
- [ ] 剩余局限已报告

---

## 19. 核心原则（Core Principle）

判断某样东西归属哪里时，使用这个模型：

```text
Rule（规则）        = 必须遵守的约束
Skill（技能）       = 如何执行一个可复用任务
Knowledge（知识）   = Agent 需要知道的东西
Profile（角色档）   = 哪些能力适用于某个角色
Agent Adapter       = 权威资产如何映射到具体 Agent
项目 AGENTS.md      = 项目级操作契约
AIHub               = 可版本化管理的控制面（Control Plane）
AIHUB_DATA          = 本地 / 私有 / 运行时数据面（Data Plane）
```

归属不清晰时，**先解决归属，再创建或修改内容**。

---

## 20. 现状清单（会过期，以实际扫描为准）

本节记录 ⬜ 项的准确状态。最后核对：**2026-09-16**。过期后应更新或删除，不留失效描述。

### 已落地

- 13 个顶层目录齐全（`.githooks` / `.github` / `.vscode` / `agents` / `config` / `docs` / `mcp` / `profiles` / `registry` / `runtime` / `scripts` / `shared` / `templates`）
- `.env`（根目录）+ `.env.example`：5 个键名已登记；`AIHUB_SKILLS` 刻意不登记（派生值，由 `scripts/lib/env.py` 计算）
- `shared/rules/` 70 个文件中 **6 个**已写好（149–199 行 / 7.3–9.8KB），**均缺 frontmatter**（§8）
- `shared/skills/` 6 个技能目录：`create-plan`、`spring-boot-ddd` 内容完整；`java-code-review`、`spring-boot` 为精简版
- 脚本：`install.py`、`fix-eol.py`、`lib/{config,deps,env}.py` 可用
- `.githooks/pre-commit` 已启用；`.github/workflows/` 下 validate 与 security-scan 两个工作流
- 6 个角色档（`profiles/*.yaml`）校验通过

### ⬜ 尚未落地

| 项 | 状态 |
|---|---|
| `shared/knowledge/`、`shared/prompts/`、`shared/memory/` | 目录存在，均为空 |
| `templates/` | 目录存在，为空 |
| `scripts/{check,doctor,security-check,sync,update,validate}.py` | 0 字节 |
| `shared/rules/INDEX.md` | 0 字节（§5.4 要求新增规则时在此登记） |
| `shared/rules/_meta/{README,rule-authoring,rule-schema}.md` | 3 个文件均 0 字节（frontmatter 规范未成文） |
| `shared/skills/engineering/{architecture-review,database-design}/SKILL.md` | 3 字节占位 |
| `registry/*.yaml` | 手工产物，与实际不符；生成器未实现（§11） |
| `${AIHUB_DATA}` 各子目录 | 均不存在 |
| `Projects/` 与项目生成能力 | 未落地（§17） |

### 已知不一致（需修）

1. **`AIHUB_DATA` 指向不存在的位置**：`.env` 里写的是 `C:\Work\AIHub_Data`，磁盘上实际存在的是 `C:\Work\AIHub_Data`（带下划线）。二者必须统一 —— 要么改 `.env`，要么改目录名。**在统一之前，脚本读到的 `AIHUB_DATA` 是一个不存在的路径。**
2. **`registry/agents.yaml` 未记录 `projects/` 与入口文件**：`claude` / `codex` 声明了 `skillMode: symlink`，但 `cursor` / `deepseek` 无此字段，与 §10 的表格一致，属待补而非错误。

### 因此

- 查不到某条规则 = 它还没写，**如实说明并按 L0 原则行事，禁止编造规则内容**；
- 引用前先验证目标文件存在且非空；
- 本节内容过期后应更新或删除。
