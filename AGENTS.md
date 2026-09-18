# AIHub — Agent 操作契约（Agent Operating Contract）

> **读者：** 在本仓库内运行的所有 AI Agent。
> **范围：** 仅限 AIHub 控制面（Control Plane）。业务项目的约定属于各项目自己的 `AGENTS.md`。
> **原则：** 规则必须是确定性的、可测试的、可执行的。含糊的指导不是规则。
> 本文件中「必须 / 禁止 / 可以 / 应当」遵循 RFC 2119 语义。
>
> **状态图例**
> ✅ 已实现 —— 已有实质内容；可用范围仍须按实际实现核对
> ⬜ 待实现 —— 路径缺失、空白或仅占位，**禁止当作已生效引用**
>
> 现状快照见 §20。引用前必须检查实际文件；快照、README 和旧注释不能代替检查。

---

## 0. 使命

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

## 1. 仓库边界

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
├── mcp/                  # ⬜ MCP 定义与示例均为占位
├── profiles/             # ✅ 角色档
├── registry/             # ⬜ 注册表（过渡期清单；目标为生成物（§11））
├── runtime/              # ✅ 本机运行时（不入库）
├── scripts/              # ✅ 工具脚本
├── shared/               # ✅ 共享事实源
└── templates/            # ⬜ 仅目录骨架，脚手架模板尚未落地
```

### AIHUB_DATA

`AIHUB_DATA` 指向**仓库之外**的本地私有数据，须独立配置。它与 `AIHUB_HOME` 是两条独立路径，无法互相推导，因此必须由dotenv环境变量（§7）单独定义。

```text
${AIHUB_DATA}/
├── local/          # 本地覆盖
├── secrets/        # 密钥
├── memory/         # 本机记忆
├── sessions/       # 会话
├── state/          # 运行时状态
├── cache/          # 缓存
├── logs/           # 日志
└── tmp/            # 临时文件
```

`AIHUB_DATA` **禁止**提交到 Git。

使用前检查外部绝对路径与权限，禁止根据示例路径移动私人数据。

---

## 2. 单一事实源规则

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
| MCP 定义 | `mcp/**` | ⬜ 占位 |
| 模板 | `templates/**` | ⬜ 空 |
| 注册表 | `registry/**` | ⬜ 过渡期输入 / 目标生成视图，见 §11 |
| 团队级结论 | `shared/memory/**` | ⬜ 空（入库） |
| 本地覆盖 | `${AIHUB_DATA}/local/**` | 本机核对 |
| 密钥 | `${AIHUB_DATA}/secrets/**` | 本机核对 |
| 本机记忆 | `${AIHUB_DATA}/memory/**` | 本机核对 |
| 运行时状态 | `${AIHUB_DATA}/state/**` | 本机核对 |

**禁止**在多个位置手工维护同一份信息。优先用引用，而不是复制。

**「记忆」的两个平面不得混用：**

- 跨会话有效、团队可共享、需要版本化的结论 → `shared/memory/`（**入库**）
- 本机私有、随时可丢的会话记忆 → `${AIHUB_DATA}/memory/`（**不入库**）

---

## 3. Hub 与项目的职责划分

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

属于**全局级**的例子：

- Java 约定
- Spring Boot 约定
- DDD 方法论
- 安全编码
- Git 约定
- Agent 行为
- 代码评审流程

---

## 4. 资产分类

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
- 密钥 → 只进入 §12 指定的私有机制，禁止写入共享资产

如果内容不适合任何一类，先弄清归属再创建。

---

## 5. 强制操作规则

### 改动前

1. **先读后动**：先读本文件，再读 `shared/rules/common/general.md`（L0）；先检查 Git 状态，保留用户已有改动。再按 `read-when` 加载相关规则；旧文件缺少元数据时，按路径、标题和任务匹配，不编造触发条件。
2. **确定场景**：确定任务类别与适用的 Profile。Hub 文档、目录和装配维护没有专用 Profile 时，使用 L0 加相关任务规则，不因默认角色是 Java 开发者而加载无关业务规则。
3. **按需加载**：只加载与任务相关的规则和技能，禁止预加载整库（§6）。
4. **先检索后创建**：创建新文件前先查看既有文件，检索是否已有等价规则或技能；发现重复时优先复用；合并超出本次范围则报告，不自行扩大改动。

### 改动中

5. **最小且内聚**：做最小连贯改动；一次提交只做一件事，禁止把重构、格式化与功能变更混在同一批改动里（保证可回滚）。
6. **先看引用方**：修改共享资产前，先确定受影响的引用方（Profile / registry / Agent 适配器）。
7. **元数据单一来源**：规则与技能的元数据以文件内 frontmatter 为准；`registry/*.yaml` 是生成物，禁止手工编辑（§8、§11）。
8. **守住体量上限**：单文件上限与 frontmatter 要求见 §8；超出部分拆到同级 `references/`。

### 完成后

9. **先验证后报告**：结果未经验证不得宣称完成；校验工具缺失或不完整时，必须如实说明该局限（§15）。
10. **留下记录**：实质性工作中可共享的结论追加到 `shared/memory/YYYY-MM-DD.md`（只追加，不回写历史）；个人进度与会话细节留在数据面。用户限定文件范围或只读分析时，不额外创建记录文件，在回复中说明。

### 红线（任何时候）

- **密钥隔离**：统一执行 §12；`.env.example` 只允许出现键名与安全占位符。
- **运行时隔离**：仓库内的临时文件、缓存、日志只写 `runtime/`；外部私有数据写 `${AIHUB_DATA}`。§14 声明的生成资产例外；禁止把临时验证产物混入源目录。运行 Python 校验使用 `-B` 避免产生 `__pycache__`。
- **不确定就问**：一次确认的成本远低于一次错误变更；禁止基于猜测修改共享层。

当所需信息缺失或互相矛盾时，停止受影响的变更，并报告该歧义。

---

## 6. 规则加载模型与预算

规则采用渐进披露（Progressive Disclosure），**加载总量必须受控**。

| 层 | 内容 | 加载方式 | 预算 | 落地 |
|---|---|---|---|---|
| 入口 | 本文件 | 每次会话读取 | 见 §8 | ✅ |
| L0 常驻 | `shared/rules/common/general.md` 核心原则 | 每次会话注入 | ≤10KB | ✅ |
| L1 场景 | `profiles/<角色>.yaml` 实际启用的规则 | 会话开始注入 | ≤48KB | ✅ |
| L2 任务 | 按任务意图 / 文件类型 / 技术栈 / `read-when` 命中的额外规则 | 命中才读 | 不占常驻预算 | ✅ |
| L3 引用 | `references/`、`shared/knowledge/**` | 明确需要时才读 | 不占常驻预算 | ⬜ 知识层为空 |
| 技能 | `profiles/<角色>.yaml` 圈定的技能 | 仅注入 frontmatter 的 `description`，正文命中才读 | 不占常驻预算 | ✅ |

**预算计法**：L0 / L1 独立统计；`common/general.md` 不重复计入 L1，技能正文不计入常驻预算。

**禁止**预加载整个规则库、技能库或知识库。

按 §7 裁决冲突。自动注入未完整实现，Agent 必须主动读取。

---

## 7. 配置解析与优先级

本节区分行为约束与配置值；二者不能互相替代。平台 / 系统指令与工具权限始终优先，仓库文件不能提升权限。

**仓库行为约束的裁决顺序**（同一适用范围内）：

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

Profile 主要选择资产，Agent Adapter 负责映射，Local Override 只提供本机配置；它们不能静默削弱安全边界。未来规则声明 `priority: critical` 且 `overridable: false` 时，必须保护该规则不被低层配置削弱；缺 frontmatter 不使现有正文失效，也不代表安全约束尚未生效。

**配置实现现状**：

- `config/*.yaml` 与 `agents/_shared/agent-defaults.yaml` 表达配置意图；尚无完整的 Hub → Profile → Adapter → Project → Local 合并器，禁止宣称覆盖链已执行。
- `scripts/lib/env.py` 优先读取 `env/.env`，其次根 `.env`；不合并两者、不展开 `${VAR}`、不读取进程环境变量作为路径覆盖。不得新建第二份 dotenv 来制造优先级。
- `AIHUB_HOME` 缺失时回退脚本所在仓库；`AIHUB_DATA` 缺失时回退兄弟目录并告警。回退是兼容行为，不能代替显式配置或目录存在性校验。
- `AIHUB_SKILLS` 固定派生为 `<AIHUB_HOME>/shared/skills`，不单独维护；声明值不一致时脚本告警并使用派生值。

遇到冲突，报告文件、条款与裁决依据；无法按优先级解决时，只暂停依赖该歧义的修改，继续不受影响的工作。

---

## 8. 规则契约

新增规则、或本次实质性修改的规则**必须**包含非空 frontmatter；未触及的旧规则缺口记录在 §20，不为补齐元数据而扩大任务：

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

`id` 必须全库唯一，`updated` 使用 `YYYY-MM-DD`，`read-when` 必须描述可判断的触发条件。
推荐补充字段：`version:` `tags:` `overridable:` `applies-to:`。字段枚举的机器校验尚未实现，不得声称已通过 schema 校验。

**体量上限**（KB 按 1024 字节、UTF-8 文件字节数计；行数和字节数均须满足，超出部分拆到同级 `references/`）：

| 对象 | 上限 |
|---|---|
| 单条规则文件 | ≤250 行 / 12KB |
| 技能 `SKILL.md` | ≤300 行 |
| 本文件（`AGENTS.md`） | ≤700 行 / 24KB |

规则必须可执行、内聚、无重复；关联规则使用引用。

旧规则的元数据缺口见 §20。

---

## 9. 技能契约

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

只建所需目录。

`SKILL.md` **必须**描述：何时适用该技能；所需输入；执行流程；预期输出；验证标准；必需的 references；相关时的权限或工具。

`references/` 里每个文件**必须**在 `SKILL.md` 正文注明「何时读」。frontmatter 的 `description` 写**触发条件**（中英双写），不写功能介绍。

详细知识放 `references/`，不要堆进一个过大的 `SKILL.md`。

---

## 10. Agent 适配器契约

`agents/<agent-id>/` 的存在只有一个目的：把 AIHub 的权威资产适配到某个 Agent 的原生配置模型。

Agent 目录**禁止**变成以下内容的独立来源：共享规则、共享技能、共享知识、密钥、运行时状态。

**已登记 Agent**（当前登记输入：`registry/agents.yaml`，见 §11）：

| id | 路径 | `skillMode` |
|---|---|---|
| `claude` | `agents/claude/` | `symlink` |
| `codex` | `agents/codex/` | `symlink` |
| `cursor` | `agents/cursor/` | 未声明 |
| `deepseek` | `agents/deepseek/` | 未声明 |

标识全仓使用上述 key。新增 Agent 必须在同一任务中明确登记来源与生成流程；生成器未实现期间遵循 §11，不手工补写生成清单来绕过缺口。

一个 Agent 适配器**可以**包含：

```text
agents/<id>/
├── AGENTS.md / CLAUDE.md   # 入口指引：只引用本文件，禁止复制其条款
├── config.yaml             # 私有配置：只写与 agent-defaults 的差异项
├── mappings.yaml           # 路径映射：源 → 目标，不做内容复制
├── skills/                 # 指向 shared/skills 的目录联接（生成物）
└── projects/               # 若使用，只存可共享的项目映射；不放业务源码
```

公共默认值集中在 `agents/_shared/agent-defaults.yaml`，各 Agent 只写差异项。

**优先使用链接、渲染或引用权威资产，而不是复制。**

`skills/` 联接由 `scripts/install.py` 装配，是**生成物**：禁止在其中新增、修改或删除文件 —— 改动会同时影响其他 Agent，也绕过 §13 的变更流程。联接不入版本库（见 `.gitignore`），换机器后重跑安装脚本并校验联接目标。

安装器只装配仓库内的技能联接，不部署 `mappings.yaml` 中的用户目录目标。映射声明不等于原生工具已支持或已加载；部署前须验证目标、格式与实际效果。扫描和统计共享技能只遍历 `shared/skills/`，禁止沿联接重复统计；删除前必须区分联接与真实目录。

---

## 11. 注册表契约

`registry/**` 的目标是生成态（generated state），**禁止**手工编辑。当前必须区分：

- `registry/agents.yaml` 是安装器实际读取的历史登记输入；它尚不能从适配器元数据重建，不能声称已有独立权威源。
- 其余清单为空或为历史手工索引，不能用来证明资产存在、启用或完整。
- 涉及登记项的新增、删除、改名时，先在任务范围内落地权威元数据和生成器；不具备条件则报告阻塞。无关的文档维护无需重新生成。

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

## 12. 安全边界

**禁止**提交：密钥、密码、令牌、Cookie、会话、私钥、凭据及敏感内网端点。

配置文件**必须间接**引用密钥。推荐写法：

```yaml
api_key_env: OPENAI_API_KEY
```

**禁止**：

```yaml
api_key: 真实密钥值
```

`.env.example` 只定义变量名和安全占位符（它是唯一键名清单，新增变量必须同步登记）。真实密钥存放于配置好的外部密钥机制或 `${AIHUB_DATA}/secrets/`。

仓库根 `.env` 是现有工具允许的本机配置入口，必须保持未跟踪；禁止将其完整内容输出到对话、日志或 diff。检查环境时只读取必要键名、路径及存在性，不打印密钥值。`.gitignore` 不能保护已经跟踪的文件，提交前必须单独检查。

**私有 Git 仓库不是密钥保险箱。**

---

## 13. 变更安全

每一次变更必须：范围明确（scoped）；可评审（reviewable）；可复现（reproducible）；可回滚（reversible）。

**禁止**混入无关的重构、格式化或配置变更。同一意图必需的源修改、依赖引用与生成结果应当原子化交付，不能以“生成文件变更必须分开”为由留下不一致状态。

重命名、移动或删除共享资产之前，检索 Profile、适配器、registry 与模板中的引用；在同一改动中更新必要依赖、重新生成受影响的生成态并验证引用。生成器缺失时按 §11 处理。

---

## 14. 生成文件

被明确标记为 generated 的文件**禁止**手工编辑，含 `registry/**`、`AIHUB_STRUCTURE.md`、`AIHUB_TREE.txt`、`agents/<id>/skills/` 联接。

生成物必须说明来源、生成器与重建命令。

如果生成输出与源状态意外不一致，**修复源或生成器，而不是修补生成输出**。

---

## 15. 校验

适用的校验通过之前，变更不算完成。

校验应当覆盖：

```text
结构 → 元数据 → 引用 → Profile → Registry → 安全 → Agent 映射
```

先检查工具实现与依赖；优先使用只读检查：

```python
python -B scripts/install.py --check-only
python -B scripts/install.py --check-only --profile java-developer
python -B scripts/fix-eol.py
git diff --check
```

- 不带 `--profile` 会跳过角色档；涉及其他角色时逐个传入实际名称，禁止将单个角色通过说成全部通过。
- 角色档和技能联接检查需要 PyYAML；`--check-only` 不禁止依赖安装提示。只读任务不得加 `--yes` 或确认安装，缺依赖时报告未完成项。
- 安装器对空引用、体积超限等仅告警，联接缺失 / 指向错误也可能只输出 INFO；退出码 0 不等于所有约束满足，必须审阅输出。
- `install.py` 未验证 frontmatter 完整性、完整映射部署、数据目录存在性或 Registry 可复现性；对本次变更相关的缺口补充只读核对。
- `fix-eol.py` 默认只报告；`--write` 会批量修改。仅改一个文件时不得为消除仓库既有告警批量格式化。
- `scripts/{validate,security-check,sync,doctor,check,update}.py` 当前为空，空脚本退出成功不能作为验证证据。
- 纯文档变更检查章节引用、事实依据、体量、换行及 diff；代码 / 配置变更按影响范围增加语法、引用和行为验证。

报告必须区分本次通过、既有问题和未验证；工具缺失不得宣称通过，不为历史缺口扩大改动。

---

## 16. Git 安全

提交之前：确认没有密钥被暂存；确认生成的 registry 已同步；确认引用可解析；审查 diff；排除无关修改。

**禁止**执行破坏性 Git 操作，除非获得明确授权。**禁止**覆盖用户的无关改动。

一次提交应当代表一个内聚的意图。

文本编码使用 UTF-8，换行策略以 `.gitattributes` 为唯一来源。只规范化本次修改的文件，禁止顺手全仓转换。

**钩子**：`.githooks/pre-commit` 检查换行符策略与密钥文件名，不能替代密钥内容扫描。`core.hooksPath` 存在 `.git/config` 里，**不随克隆分发** —— 换机器或重新克隆后**必须**重设：

```sh
git config core.hooksPath .githooks
```

---

## 17. 项目生成

项目生成是规划能力，当前模板尚未实现；落地后生成的业务项目**不归** AIHub 仓库所有。

项目默认输出位置在 `AIHUB_HOME` 之外，例如：

```text
C:\Work\
├── AIHub\                  # 控制面
├── AIHub_Data\             # 数据面（本地私有，不入库）
└── AIHub_Workspace\        # ⬜ 生成的项目，尚未落地
    ├── order-service\
    └── payment-service\
```

生成的项目应当包含自己的 `AGENTS.md`、`.agents/`、`docs/`。项目级规则与知识留在项目里。

可复用的改进应当**有意识地**反哺回 AIHub，**禁止**自动回流。

---

## 18. 完成定义

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

## 19. 核心原则

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

最后核对：**2026-09-17**。统计排除 `.git/`、`runtime/`、Python 缓存与技能联接；空目录不随 Git 克隆保留。

### 已有实质内容

- 顶层 13 个目录存在（不计 `.git`），目录存在不等于内容或功能可用。
- 根 `.env` 的 5 个键名均登记于 `.env.example`；`AIHUB_SKILLS` 由 `scripts/lib/env.py` 派生。
- `shared/rules/` 共 70 个文件（含 INDEX 与 `_meta`），6 个有正文、64 个为空。6 个正文均缺 frontmatter。
- `shared/skills/` 共 6 个 `SKILL.md`：`create-plan`、`spring-boot-ddd` 有工作流正文；`java-code-review`、`spring-boot` 为精简版；另外 2 个为 3 字节占位。不是所有技能子目录都有入口文件。
- `profiles/` 有 6 个角色档；`product-manager` 与 `tester` 当前只引用 L0，不代表产品 / 测试能力完整。是否通过校验必须以本次执行结果为准。
- `install.py`、`fix-eol.py`、`scripts/lib/{config,deps,env}.py` 有实现；适用范围与限制见 §7、§15。
- Agent 公共默认值、Claude / Codex 配置及入口、四个 Agent 的映射声明均存在；声明不等于完成部署。
- `.githooks/pre-commit` 与两个 CI 工作流存在。`validate.yaml` 目前只显式校验 `java-developer`；`security-scan.yaml` 配置 gitleaks 与跟踪文件守卫，配置存在不等于本次运行成功。

### 待实现 / 仅骨架

| 项 | 实测状态 |
|---|---|
| `shared/knowledge/`、`shared/prompts/`、`templates/` | 有子目录骨架，无文件 |
| `shared/memory/` | 空目录 |
| `mcp/servers.yaml`、`mcp/profiles/*.yaml`、`mcp/examples/mcp.local.example.json` | 共 5 个文件，均为 0 字节 |
| `scripts/{check,doctor,security-check,sync,update,validate}.py` | 均为 0 字节 |
| `shared/rules/INDEX.md`、`shared/rules/_meta/*.md` | 共 4 个文件，均为 0 字节，不作生效规范引用 |
| `shared/skills/engineering/{architecture-review,database-design}/SKILL.md` | 3 字节占位，无可执行工作流 |
| `registry/{mcp,profiles}.yaml` | 0 字节 |
| `registry/{agents,rules,skills}.yaml` | 历史手工清单，无可复现生成器；过渡规则见 §11 |
| 项目模板生成、配置合并、原生目录部署 | 尚无完整实现，不得仅据目录 / YAML 声称可用 |

### 已核实的漂移与限制

1. 原 `AIHUB_DATA` 不存在的结论已失效：外部目录及 §1 列出的子目录均存在，仅核对路径，未读取私有内容。
2. `README.md`、Agent 入口、Profile 和脚本中的部分章节号及状态描述已过期；例如入口仍称配置为占位。按本文件的章节标题与实际文件核对，不据旧编号推导规则。
3. `registry/rules.yaml` 仍引用空的 `security/secrets.md`，证明历史索引不能替代源检查；`registry/agents.yaml` 的 cursor / deepseek 未声明 `skillMode`，安装器会跳过其技能联接。
4. `docs/` 下文档及根目录结构草稿不作为当前目录事实源；结构以实际扫描为准，生成物按 §14 处理。

查不到规则或只找到占位时，如实报告并按 L0 与本契约执行。仅在本次任务授权范围内更新关联文件；其余漂移留待后续任务。
