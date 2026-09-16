# 目录结构
```
c:/AiHub/
├─ shared/                    # 跨 Agent 共用的唯一事实源
│  ├─ skills/                 # 公共 Skill 库（建议作为独立 git 仓库）
│  ├─ rules/                  # 通用规则：编码、命名、提交规范
│  ├─ knowledge/              # 领域文档、API 手册、业务背景
│  ├─ memory/                 # 长期记忆、项目日志
│  └─ prompts/                # 通用提示词片段
├─ agents/                    # 每个 Agent 一个隔离工作区
│  ├─ workbuddy/
│  │  ├─ CLAUDE.md            # 该 Agent 的规则入口
│  │  ├─ .workbuddy/          # 平台私有配置、memory
│  │  ├─ skills/              # → 符号链接到 shared/skills
│  │  └─ projects/            # 该 Agent 产出物
│  ├─ cursor/
│  ├─ claude-code/
│  └─ codex/
├─ mcp/                       # MCP server 配置集中一处
│  └─ mcp.json
├─ env/                       # .env.example（密钥绝不入版本库）
└─ scripts/                   # 初始化 / 同步脚本
```


# 环境变量
AIHUB_SKILLS = c:/AiHub/shared/skills