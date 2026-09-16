# codex — AIHub 入口

> 读者：在 `agents/codex/` 下工作的 Codex。
> Hub 维护约定以仓库根 `AGENTS.md` 为准；本文件只做入口指引，不重复其条款（根 `AGENTS.md` §1.5 禁止复制）。

## 必读顺序

1. 仓库根 `AGENTS.md` —— Hub 级约定，每次会话必读，全文注入。
2. `registry/agents.yaml` —— 本 Agent 的登记项（`enabled` / `path` / `skillMode`）。
3. 按根 `AGENTS.md` §1.1「先读后动」命中本次任务的规则文件。

## 本目录

| 路径 | 用途 | 归属 |
|---|---|---|
| `skills/` | 指向 `shared/skills` 的目录联接，由 `scripts/install.py` 装配 | 生成物，**禁止写入** |
| `mappings.yaml` | 本 Agent 的路径映射 | 本目录私有 |
| `config.yaml` | 本 Agent 的私有配置 | 本目录私有 |
| `projects/` | 产出物落盘位置 | 本目录私有 |

`skills/` 不是独立副本：同一份技能由 `shared/skills` 单一维护，本目录出现的只是联接。因此**不要在这里新增、修改或删除文件**——改动会同时影响其他 Agent，也绕过了根 `AGENTS.md` §4 的变更流程。

## 边界

- 只写 `agents/codex/` 与 `runtime/`；不写其他 Agent 目录。
- 不编辑 `shared/`：写入只走根 `AGENTS.md` §4 的变更流程。
- 不改 `registry/*.yaml`、`AIHUB_STRUCTURE.md`、`AIHUB_TREE.txt`（生成物，见根 `AGENTS.md` §7.1）。
- 提交前不引入密钥、token、内网地址。

## 现状

`config.yaml` / `mappings.yaml` 等仍为未填写的占位；引用任何目标前先确认其存在且非空（根 `AGENTS.md` §7.5），查不到就如实说明，不要编造。
