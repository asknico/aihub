# C:\Work\AIHub 目录结构树

> 生成时间：2026-09-14
> 统计：8 个一级目录 / 41 个子目录 / 21 个文件（其中 19 个为占位符，待填充）

```
C:\Work\AIHub
│
├── AGENTS.md                          # 总入口：目录结构说明 + 环境变量约定（1190B，有效内容）
├── README.md                          # 同 AGENTS.md（目前内容重复，建议 README 写简介、AGENTS.md 写规则）
│
├── shared\                            # 跨 Agent 共享层 —— 单一事实源
│   ├── skills\                        # 公共 Skill 库（建议独立 git 仓库 / submodule）
│   │   ├── common\                    # 通用能力（所有 Agent 可用）
│   │   │   ├── documentation\         # · 文档撰写 —— 空
│   │   │   ├── task-planning\         # · 任务拆解与计划 —— 空
│   │   │   └── web-research\          # · 联网调研 —— 空
│   │   ├── devops\                    # 运维与交付
│   │   │   ├── docker\                # · 容器化 —— 空
│   │   │   ├── github-actions\        # · CI/CD 流水线 —— 空
│   │   │   └── kubernetes\            # · K8s 编排 —— 空
│   │   ├── engineering\               # 研发工程（已建 SKILL.md 骨架）
│   │   │   ├── architecture-review\   # · 架构评审        [SKILL.md 占位]
│   │   │   ├── database-design\       # · 数据库设计      [SKILL.md 占位]
│   │   │   ├── java-code-review\      # · Java 代码审查   [SKILL.md 占位]
│   │   │   │   ├── examples\          #   · 示例代码 —— 空
│   │   │   │   ├── references\        #   · 参考资料 —— 空
│   │   │   │   └── scripts\           #   · 辅助脚本 —— 空
│   │   │   └── spring-boot\           # · Spring Boot 开发 [SKILL.md 占位]
│   │   ├── product\                   # 产品侧
│   │   │   ├── prd-review\            # · PRD 评审 —— 空
│   │   │   └── requirement-analysis\  # · 需求分析 —— 空
│   │   ├── qtp-ddd\                   # · DDD 领域驱动设计（QTP 项目域）—— 空
│   │   └── testing\                   # 测试
│   │       ├── api-testing\           # · 接口测试 —— 空
│   │       ├── test-case-design\      # · 用例设计 —— 空
│   │       └── unit-testing\          # · 单元测试 —— 空
│   ├── rules\                         # 全局规则（按领域分）
│   │   ├── architecture\              # · 架构规范 —— 空
│   │   ├── coding\                    # · 编码规范 —— 空
│   │   ├── git\                       # · 提交与分支规范 —— 空
│   │   └── security\                  # · 安全规范 —— 空
│   ├── knowledge\                     # 领域文档 / API 手册 / 业务背景 —— 空
│   ├── memory\                        # 长期记忆 / 项目日志 —— 空
│   └── prompts\                       # 通用提示词片段
│       ├── architecture\              # · 架构类 —— 空
│       ├── coding\                    # · 编码类 —— 空
│       ├── product\                   # · 产品类 —— 空
│       ├── system\                    # · 系统提示词 —— 空
│       └── testing\                   # · 测试类 —— 空
│
├── agents\                            # 各 Agent 隔离工作区
│   ├── claud\                         # Claude Code 工作区
│   │   ├── CLAUDE.md                  #   规则入口      [占位 3B]
│   │   └── config.yaml                #   私有配置      [占位 2B]
│   ├── codex\                         # Codex CLI 工作区
│   │   ├── CODEX.md                   #   规则入口      [占位 3B]
│   │   └── config.yaml                #   私有配置      [占位 2B]
│   ├── cursor\                        # Cursor 工作区 —— 空
│   └── deepseek\                      # DeepSeek 工作区 —— 空
│
├── config\                            # 全局配置（跨 Agent 共用）
│   ├── global.yaml                    #   全局设置      [占位 2B]
│   ├── mcp.yaml                       #   MCP 开关      [占位 2B]
│   ├── models.yaml                    #   模型路由      [占位 2B]
│   └── permissions.yaml               #   权限策略      [占位 2B]
│
├── mcp\                               # MCP Server 配置集中管理
│   ├── mcp.json                       #   MCP 主配置    [占位 3B]
│   ├── servers.yaml                   #   Server 清单   [占位 3B]
│   └── profiles\                      #   按场景的配置档 —— 空
│
├── templates\                         # 项目脚手架模板
│   ├── java\                          #   Java 项目模板 —— 空
│   ├── microservice\                  #   微服务模板 —— 空
│   └── spring-boot\                   #   Spring Boot 模板 —— 空
│
├── env\                               # .env.example（密钥不入版本库）—— 空
│
└── scripts\                           # 初始化与同步脚本
    ├── check.psl                      #   环境检查      [占位 3B]
    ├── install.psl                    #   安装初始化    [占位 3B]
    ├── sync.psl                       #   Skill 同步    [占位 3B]
    └── update.psl                     #   批量更新      [占位 3B]
```

## 环境变量约定

```
AIHUB_SKILLS = C:/Work/AIHub/shared/skills
```

## 现状小结

| 项目 | 数量 | 说明 |
|---|---|---|
| 一级目录 | 8 | shared / agents / config / mcp / templates / env / scripts |
| 目录总数 | 41 | 含嵌套子目录 |
| 文件总数 | 21 | 其中 19 个是占位内容 |
| 空目录 | 33 | 已建骨架，等待填充 |

## 待处理事项

1. **占位文件**：19 个文件内容是 `ss` / `sss` / `sxx` 等测试字符，需要替换为真实内容。
2. **目录命名**：`claud` 疑似 `claude` 拼写遗漏，建议改为 `claude-code`（与 `CLAUDE.md` 一致）。
3. **规则文件名**：`codex/CODEX.md` 建议改为 `AGENTS.md`（Codex 官方约定），或与根目录一致。
4. **空目录未纳入 git**：Git 不跟踪空目录，需要 `templates/`、`shared/` 等空目录放 `.gitkeep` 才能提交。
5. **README.md 与 AGENTS.md 内容完全重复**（都是 1190B 同一份），建议拆分职责。
