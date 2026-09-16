# AIHub

**AI Agent 配置资产的统一管理枢纽（控制面）。** 用一个 Git 仓库集中管理规则（Rules）、技能（Skills）、角色档（Profiles）、Agent 适配器与 MCP 定义，让多个 AI 编码 Agent（Claude Code、Codex、Cursor、DeepSeek…）共享同一份事实源，而不是各自维护一套漂移的配置。

- **版本**：见 [VERSION](VERSION)（当前 `0.1.0`）
- **Agent 行为契约**：[AGENTS.md](AGENTS.md) —— 本仓库的最高约束文件，定义仓库边界、单一事实源、加载预算与安全红线。**改动本仓库前必读。**
- **人类读者看本文件；Agent 读者看 AGENTS.md。**

---

## 1. 设计原则

| 原则 | 含义 |
|---|---|
| **单一事实源** | 每个概念有且只有一个权威位置；其余地方只引用、不复制 |
| **控制面 / 数据面分离** | 可版本化的资产入库（本仓库）；密钥、会话、记忆、缓存等本机私有数据放仓库外的 `${AIHUB_DATA}` |
| **渐进披露** | 规则按 L0（常驻）→ L1（场景）→ L2（按需）分层加载，禁止预加载整库，常驻预算受控 |
| **生成物不手改** | `registry/**`、`agents/*/skills/` 联接等由脚本生成，能从源完整复现 |

---

## 2. 目录结构与职责

```text
AIHub/
├── AGENTS.md              # Agent 操作契约（最高约束，入口文件）
├── README.md              # 本文件（人类读者入口）
├── .env.example           # 环境变量唯一键名清单（.env 从它复制，不入库）
├── VERSION                # 语义化版本号
│
├── shared/                # ★ 共享事实源（所有 Agent 共用，只读权威）
│   ├── rules/             #   强制规则，按领域分层：common/ coding/ architecture/
│   │   │                  #   ai/ api/ database/ devops/ git/ security/ testing/
│   │   └── _meta/         #   规则元规范（schema、写作指南）⬜ 待成文
│   ├── skills/            #   可复用任务技能，按域分组：common/ engineering/
│   │   │                  #   devops/ product/ testing/
│   │   └── <domain>/<skill>/   # SKILL.md + references/ + examples/ + tests/
│   ├── knowledge/         #   稳定可复用知识 ⬜ 目录已建，内容为空
│   ├── prompts/           #   可复用提示词片段 ⬜ 目录已建，内容为空
│   └── memory/            #   团队级结论沉淀（入库）⬜ 目录已建，内容为空
│
├── agents/                # 各 Agent 适配器（把权威资产映射到原生配置）
│   ├── _shared/           #   agent-defaults.yaml：公共默认值
│   ├── claude/            #   CLAUDE.md 入口 + config.yaml + mappings.yaml
│   ├── codex/             #   AGENTS.md 入口 + config.yaml + mappings.yaml
│   ├── cursor/            #   mappings.yaml（Cursor 无独立入口文件约定）
│   ├── deepseek/          #   mappings.yaml
│   └── <id>/skills/       #   → shared/skills 的目录联接（install.py 生成，不入库）
│
├── profiles/              # 角色档：某角色加载哪些规则/技能（6 个，校验通过）
│                          #   java-developer / springboot-ddd / architect /
│                          #   fullstack / product-manager / tester
├── config/                # Hub 级配置：global / features / models / permissions
├── mcp/                   # MCP 定义：servers.yaml + profiles/（按场景的组合）
├── registry/              # 注册表（生成物，禁止手改）⬜ 生成器未实现，暂为手工产物
├── templates/             # 项目/技能脚手架模板 ⬜ 目录已建，内容为空
├── scripts/               # 工具脚本（见 §4）
├── docs/                  # 文档 ⬜ 现存 3 份为过期草稿，待重写
├── runtime/               # 本机运行时（不入库）：cache/ logs/ sessions/ tmp/ …
│
├── .githooks/             # pre-commit 钩子（换行符策略 + 密钥文件名拦截）
├── .github/               # CI 工作流（validate / security-scan）、CODEOWNERS、dependabot
└── .vscode/               # 编辑器配置示例
```

图例：⬜ = 目录存在但内容未落地；引用前先核对 [AGENTS.md §20](AGENTS.md) 的现状清单。

---

## 3. 快速开始

### 3.1 环境变量

```sh
cp .env.example .env        # 然后填入真实密钥
```

| 变量 | 说明 |
|---|---|
| `AIHUB_HOME` | 本仓库根路径（如 `C:\Work\AIHub`） |
| `AIHUB_DATA` | 仓库外的本机数据目录（密钥/会话/缓存/记忆），**不入库** |
| `AIHUB_SKILLS` | 无需登记 —— 由 `scripts/lib/env.py` 从 `AIHUB_HOME` 派生（`<AIHUB_HOME>/shared/skills`） |

真实密钥只放 `.env`（已被 `.gitignore` 排除）；配置文件中只允许 `api_key_env: XXX_KEY` 式的间接引用。**私有仓库不是密钥保险箱。**

### 3.2 初始化装配

依赖 Python ≥ 3.8（仅需标准库；PyYAML 缺失时脚本会提示，经确认后自动安装）：

```sh
python scripts/install.py              # 建目录骨架、校验配置、装配技能联接（幂等）
python scripts/install.py --check-only # 只体检，不改动
python scripts/fix-eol.py              # 换行符策略体检（--write 才改写）
```

`install.py` 会把 `agents/claude/skills`、`agents/codex/skills` 建为指向 `shared/skills` 的目录联接（Windows junction / Unix symlink）——**联接是本机生成物，禁止在其中直接改文件**，改动请到 `shared/skills/`。

### 3.3 启用 Git 钩子（换机器后必须重做一次）

`core.hooksPath` 存在本机 `.git/config` 里，不随克隆分发：

```sh
git config core.hooksPath .githooks
```

钩子做两件事：拦截 CRLF 违规文件、拦截密钥类文件名进入暂存区。

---

## 4. 工具脚本

| 脚本 | 状态 | 用途 |
|---|---|---|
| `scripts/install.py` | ✅ | 环境检测 → 目录骨架 → 配置校验 → 角色档校验 → 技能联接装配（幂等） |
| `scripts/fix-eol.py` | ✅ | 换行符规范化：策略解析自 `.gitattributes`；默认只报告，`--write` 才改写 |
| `scripts/lib/{env,config,deps}.py` | ✅ | 路径派生 / YAML 加载 / 依赖检测的公共库 |
| `scripts/{validate,check,doctor,sync,update,security-check}.py` | ⬜ | 占位未实现（0 字节）。规则/技能元数据校验与 registry 生成尚缺 |

CI（`.github/workflows/`）：`validate.yaml` 跑库内体检与语法检查；`security-scan.yaml` 跑 gitleaks 全历史扫描与仓库守卫。

---

## 5. 在业务项目中使用

AIHub 定义「Agent 应当如何工作」；业务仓库定义「项目是什么」。项目侧**引用**而不**复制**共享规则：

- 项目的 `AGENTS.md` 按角色档（`profiles/*.yaml`）圈定要加载的规则与技能；
- 项目专属约束（限界上下文、业务不变量、API 约定等）写在项目自己的规则里；
- 通用改进应有意识地反哺回 AIHub 的 `shared/`，禁止自动回流。

生成的业务项目放在 `AIHUB_HOME` 之外（如 `C:\Work\Projects\`），不归本仓库所有。

---

## 6. 文档导航

| 文档 | 读者 | 状态 |
|---|---|---|
| [AGENTS.md](AGENTS.md) | Agent / 维护者（契约 0–20 节，含现状清单 §20） | ✅ 权威 |
| [README.md](README.md)（本文件） | 人类读者 | ✅ 权威 |
| `.env.example` | 配置环境 | ✅ 权威（唯一键名清单） |
| `docs/CONTRIBUTING.md`、`docs/SECURITY.md`、`docs/AIHUB_STRUCTURE.md` | — | ⬜ 过期草稿，待重写，勿引用 |
| `AIHUB_STRUCTURE.md`、`AIHUB_TREE.txt`（根目录） | — | ⬜ 生成物草稿，待 sync 脚本接管 |

## 7. 已知限制

详见 [AGENTS.md §20](AGENTS.md)（以实际扫描为准）。要点：

1. `shared/rules/` 70 个文件中仅 6 个已写好，且均缺 frontmatter（§8 契约未生效）；
2. `registry/*.yaml` 为早期手工产物，与实际状态不符，生成器（`sync.py`）未实现；
3. `${AIHUB_DATA}` 指向的目录尚未创建；
4. `docs/` 三份文档为过期草稿；
5. `knowledge/`、`prompts/`、`memory/`、`templates/` 为空目录，属规划位。

## 8. 贡献

改本仓库前先读 [AGENTS.md](AGENTS.md)，尤其：§5 强制操作规则、§13 变更安全（一次提交只做一件事）、§12 安全边界。新增环境变量必须同步登记 `.env.example`；新增 Agent 必须先登记 `registry/agents.yaml` 再建目录。
