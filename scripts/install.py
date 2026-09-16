#!/usr/bin/env python3
"""install.py — AIHub 初始化 / 校验脚本（Windows / macOS / Linux 通用）

五个步骤
    1. 解析 .env，派生全部路径
    2. 检查目录骨架，补齐缺失目录
    3. 从 .example 生成配置文件，并校验键名登记完整性
    4. 读取角色档，校验引用有效性、单文件上限与 L0/L1 预算
    5. 为各 Agent 建立指向 shared/skills 的目录联接

依赖策略
    步骤 1-3（路径解析、目录骨架、配置文件）只用标准库。
    步骤 4、5 需要读 YAML（角色档与 registry/agents.yaml），因此会用到
    PyYAML —— 但只在真正读到时才请求安装，不会在脚本启动时就索要依赖。
    未安装时这两步会明确报错退出，而不是静默跳过或编造内容。

幂等性
    重复执行只补齐缺失部分，不覆盖已有内容。覆盖行为必须显式：
    重建联接要 `--force`，生成配置要文件不存在。

用法
    python3 scripts/install.py                      # 完整初始化（不校验角色档）
    python3 scripts/install.py --check-only         # 只读体检，不写任何文件
    python3 scripts/install.py --profile java-developer
    python3 scripts/install.py --force              # 重建指向错误的联接
"""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from lib import env                                    # noqa: E402
from lib.config import ConfigError, load_yaml          # noqa: E402

# AGENTS.md §4 要求角色档只引用「实际存在且非空」的规则；这里保证关键目录齐全。
REQUIRED_DIRS = (
    "agents",
    "config",
    "mcp",
    "profiles",
    "registry",
    "runtime",
    "scripts",
    "shared/knowledge",
    "shared/memory",
    "shared/prompts",
    "shared/rules",
    "shared/skills",
    "templates",
)

# AGENTS.md §2：L0「常驻」层预算 ≤10KB
L0_BUDGET_BYTES = 10 * 1024

# AGENTS.md §2：L1「场景」层预算 ≤48KB
# 注意只统计规则文件 —— 技能走渐进披露（会话期只注入 frontmatter 的
# description，正文命中才加载），因此不占用常驻预算。
L1_BUDGET_BYTES = 48 * 1024

# AGENTS.md §1.4：单个规则文件上限 250 行 / 12KB
RULE_MAX_BYTES = 12 * 1024
RULE_MAX_LINES = 250

# L0 层就是这一个文件。角色档里列它只为显式声明依赖，
# 统计时归入 L0，不重复计入 L1 —— 否则同一份内容会被两处预算各算一遍。
L0_RULES = frozenset({"common/general.md"})

# 占位文件的特征长度：仓库里大量文件内容是 "ss" / "sss" 之类的测试字符
PLACEHOLDER_MAX_BYTES = 3


# --------------------------------------------------------------------------
# 输出
# --------------------------------------------------------------------------
class UI:
    """统一的结果输出与计数。

    所有步骤通过它报告结果，避免每个函数各自 print 出不同格式。
    """

    def __init__(self) -> None:
        self.failures: list[str] = []
        self.warnings: list[str] = []

    def head(self, text: str) -> None:
        print(f"\n[{text}]")

    def ok(self, message: str, detail: list[str] | None = None) -> None:
        self._emit("OK", message, detail)

    def skip(self, message: str, detail: list[str] | None = None) -> None:
        self._emit("SKIP", message, detail)

    def info(self, message: str, detail: list[str] | None = None) -> None:
        self._emit("INFO", message, detail)

    def warn(self, message: str, detail: list[str] | None = None) -> None:
        self.warnings.append(message)
        self._emit("WARN", message, detail)

    def fail(self, message: str, detail: list[str] | None = None) -> None:
        self.failures.append(message)
        self._emit("FAIL", message, detail)

    @staticmethod
    def _emit(tag: str, message: str, detail: list[str] | None) -> None:
        print(f"  [{tag:^4}] {message}")
        for line in detail or []:
            print(f"         {line}")


def _force_utf8_stdio() -> None:
    """Windows 下把标准输出固定为 UTF-8。

    输出被重定向到文件时，Python 会退回 locale 编码（中文环境是 cp936），
    此时打印中文可能直接 UnicodeEncodeError 崩掉。
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8")
        except (OSError, ValueError):
            pass


# --------------------------------------------------------------------------
# 步骤 1：环境与路径
# --------------------------------------------------------------------------
def step_environment(paths: env.Paths, ui: UI, warnings: list[str]) -> None:
    ui.head("1/5  环境与路径")
    print(f"         root    {paths.root}")
    print(f"         skills  {paths.skills}")
    print(f"         data    {paths.data}")
    print(f"         env     {paths.env_file or '（未找到）'}")

    for message in warnings:
        ui.warn(message)
    if not warnings:
        ui.ok("环境变量解析完成，无异常")

    if not (paths.root / "shared").is_dir():
        ui.fail(f"{paths.root} 下没有 shared/，AIHUB_HOME 可能配置有误")


# --------------------------------------------------------------------------
# 步骤 2：目录骨架
# --------------------------------------------------------------------------
def step_skeleton(paths: env.Paths, ui: UI, *, check_only: bool) -> None:
    ui.head("2/5  目录骨架")

    missing = [d for d in REQUIRED_DIRS if not (paths.root / d).is_dir()]

    if not missing:
        ui.ok(f"{len(REQUIRED_DIRS)} 个必需目录齐全")
    elif check_only:
        ui.fail(f"缺少 {len(missing)} 个必需目录", missing)
    else:
        created: list[str] = []
        for rel in missing:
            try:
                (paths.root / rel).mkdir(parents=True, exist_ok=True)
                created.append(rel)
            except OSError as exc:
                ui.fail(f"创建 {rel} 失败：{exc}")
        if created:
            ui.ok(f"已补齐 {len(created)} 个目录", created)

    empty = [
        rel
        for rel in REQUIRED_DIRS
        if (paths.root / rel).is_dir() and not any((paths.root / rel).iterdir())
    ]
    if empty:
        ui.info(
            f"{len(empty)} 个目录为空 —— git 不跟踪空目录，"
            "将来 git init 后需要 .gitkeep 占位",
            empty,
        )


# --------------------------------------------------------------------------
# 步骤 3：配置文件
# --------------------------------------------------------------------------
def step_configs(paths: env.Paths, ui: UI, *, check_only: bool) -> None:
    ui.head("3/5  配置文件")

    target = paths.root / ".env"
    if paths.env_file is not None:
        ui.skip(f"{paths.env_file.relative_to(paths.root)} 已存在")
    elif not paths.env_example.is_file():
        ui.fail("缺少 .env.example，无法生成 .env")
    elif check_only:
        ui.fail("缺少 .env（应由 .env.example 复制而来）")
    else:
        try:
            shutil.copyfile(paths.env_example, target)
            ui.ok("已从 .env.example 生成 .env")
        except OSError as exc:
            ui.fail(f"生成 .env 失败：{exc}")

    # AGENTS.md §6：.env.example 是唯一键名清单，新增变量必须同步登记。
    # 这一条最容易被违反 —— 真实值加了新变量，模板却忘了加。
    if paths.env_file is not None and paths.env_example.is_file():
        actual = set(env.parse_dotenv(paths.env_file.read_text(encoding="utf-8")))
        declared = set(env.parse_dotenv(paths.env_example.read_text(encoding="utf-8")))
        undeclared = sorted(actual - declared)
        if undeclared:
            ui.warn(
                f"{len(undeclared)} 个键在 .env 里存在但未登记到 .env.example"
                "（AGENTS.md §6 要求同步登记）",
                undeclared,
            )
        else:
            ui.ok(f"{len(actual)} 个键均已登记在 .env.example")


# --------------------------------------------------------------------------
# 步骤 4：角色档校验（唯一需要 PyYAML 的步骤）
# --------------------------------------------------------------------------
def _find_skill(skills_root: Path, name: str) -> Path | None:
    """按技能目录名定位 SKILL.md。

    技能可以嵌在任意域层级下（engineering/、common/…），
    所以按目录名做一次递归匹配，而不是假设固定深度。
    """
    if not skills_root.is_dir():
        return None
    for skill_md in sorted(skills_root.rglob("SKILL.md")):
        if skill_md.parent.name == name:
            return skill_md
    return None


def _file_lines(path: Path) -> int:
    """统计行数。读失败时返回 0 而不抛异常 —— 行数只是提示信息，不该中断体检。"""
    try:
        return len(path.read_text(encoding="utf-8", errors="replace").splitlines())
    except OSError:
        return 0


def step_profile(
    paths: env.Paths, ui: UI, name: str, *, auto: bool
) -> None:
    ui.head(f"4/5  角色档 {name}")

    profile_path = paths.profiles / f"{name}.yaml"
    try:
        data = load_yaml(profile_path, auto=auto)
    except ConfigError as exc:
        ui.fail(str(exc))
        return

    rule_refs = [r for r in (data.get("rules") or []) if isinstance(r, str)]
    skill_refs = [s for s in (data.get("skills") or []) if isinstance(s, str)]

    if not rule_refs and not skill_refs:
        ui.warn(f"{name}.yaml 既未引用规则也未引用技能")
        return

    missing: list[str] = []
    empty: list[str] = []
    oversized: list[str] = []
    l0_refs = l0_total = 0
    l1_refs = l1_total = 0

    for ref in rule_refs:
        path = paths.rules / ref
        if not path.is_file():
            missing.append(f"{ref}   （文件不存在）")
            continue

        size = path.stat().st_size
        if size <= PLACEHOLDER_MAX_BYTES:
            empty.append(f"{ref}   （空文件或占位）")
            continue

        lines = _file_lines(path)
        if size > RULE_MAX_BYTES or lines > RULE_MAX_LINES:
            oversized.append(f"{ref}   {lines} 行 / {size / 1024:.1f} KB")

        if ref in L0_RULES:
            l0_refs += 1
            l0_total += size
        else:
            l1_refs += 1
            l1_total += size

    # 技能走渐进披露：会话期只注入 frontmatter 的 description，正文命中才加载。
    # 因此这里只校验存在性与非空，不把体积计入常驻预算。
    for ref in skill_refs:
        found = _find_skill(paths.skills, ref)
        if found is None:
            missing.append(f"{ref}   （技能目录不存在）")
        elif found.stat().st_size <= PLACEHOLDER_MAX_BYTES:
            empty.append(f"{ref}   （SKILL.md 为空或占位）")

    ui.info(
        f"引用 {len(rule_refs)} 条规则（L0×{l0_refs} + L1×{l1_refs}）"
        f" + {len(skill_refs)} 个技能"
    )
    ui.info(
        f"加载量  L0 {l0_total / 1024:.1f} KB / {L0_BUDGET_BYTES / 1024:.0f} KB"
        f"    L1 {l1_total / 1024:.1f} KB / {L1_BUDGET_BYTES / 1024:.0f} KB"
    )

    if missing:
        ui.fail(f"{len(missing)} 个引用指向不存在的目标", missing)
    if empty:
        ui.warn(
            f"{len(empty)} 个引用指向空文件 —— AGENTS.md §7.5 禁止"
            "把尚未填写的文件当作已生效",
            empty,
        )
    if oversized:
        ui.warn(
            f"{len(oversized)} 个规则文件超出单文件上限 "
            f"{RULE_MAX_LINES} 行 / {RULE_MAX_BYTES / 1024:.0f} KB"
            "（AGENTS.md §1.4，超出部分应拆到 references/）",
            oversized,
        )

    budgets_ok = l0_total <= L0_BUDGET_BYTES and l1_total <= L1_BUDGET_BYTES
    if l0_total > L0_BUDGET_BYTES:
        ui.warn(
            f"L0 加载量 {l0_total / 1024:.1f} KB 超出预算 "
            f"{L0_BUDGET_BYTES / 1024:.0f} KB（AGENTS.md §2 加载链）"
        )
    if l1_total > L1_BUDGET_BYTES:
        ui.warn(
            f"L1 加载量 {l1_total / 1024:.1f} KB 超出预算 "
            f"{L1_BUDGET_BYTES / 1024:.0f} KB（AGENTS.md §2 加载链）"
        )

    if not missing and not empty and not oversized and budgets_ok:
        ui.ok("全部引用有效，未超出单文件上限与 L0/L1 预算")


# --------------------------------------------------------------------------
# 步骤 5：Agent 技能联接
# --------------------------------------------------------------------------
def _is_reparse_point(path: Path) -> bool:
    """判断路径是否为联接 / 符号链接。

    必须区分「联接」与「真实目录」：前者可以安全重建，后者绝对不能动。
    Windows 的 junction 不算 symlink（Path.is_symlink() 返回 False），
    而 Path.is_junction() 要 Python 3.12+，所以这里直接看 reparse 属性。
    """
    if sys.platform != "win32":
        return path.is_symlink()
    try:
        st = os.lstat(path)
    except OSError:
        return False
    return bool(getattr(st, "st_reparse_tag", 0)) or stat.S_ISLNK(st.st_mode)


def _points_to(link: Path, source: Path) -> bool:
    try:
        return link.resolve() == source.resolve()
    except OSError:
        return False


def _make_link(link: Path, source: Path) -> str | None:
    """创建目录联接。成功返回 None，失败返回错误描述。"""
    if sys.platform == "win32":
        # junction 不需要管理员权限，也比 symlink 可靠
        proc = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(source)],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            return (proc.stdout or proc.stderr or "mklink 失败").strip()
        return None

    try:
        link.symlink_to(source, target_is_directory=True)
    except OSError as exc:
        return str(exc)
    return None


def _ensure_link(
    link: Path,
    source: Path,
    ui: UI,
    *,
    label: str,
    force: bool,
    check_only: bool,
) -> None:
    rel = f"agents/{label}/skills"

    if not source.is_dir():
        ui.fail(f"联接源不存在：{source}")
        return

    if link.exists() or link.is_symlink():
        if _points_to(link, source):
            ui.skip(f"{rel} 已正确指向 shared/skills")
            return

        if not _is_reparse_point(link):
            # 真实目录：绝不删除。宁可停下让人来看。
            ui.fail(f"{rel} 是真实目录而非联接，已跳过（请人工确认后再处理）")
            return

        if check_only:
            ui.info(f"{rel} 是指向别处的联接，需要重建")
            return
        if not force:
            ui.warn(f"{rel} 指向别处，未改动（加 --force 可重建）")
            return

        try:
            link.rmdir() if link.is_dir() else link.unlink()
        except OSError as exc:
            ui.fail(f"删除旧联接 {rel} 失败：{exc}")
            return

    if check_only:
        ui.info(f"{rel} 待创建 → shared/skills")
        return

    link.parent.mkdir(parents=True, exist_ok=True)
    error = _make_link(link, source)
    if error:
        ui.fail(f"{rel} 创建失败：{error}")
    else:
        ui.ok(f"{rel} → shared/skills")


def step_links(
    paths: env.Paths, ui: UI, *, force: bool, check_only: bool, auto: bool
) -> None:
    ui.head("5/5  Agent 技能联接")

    registry_path = paths.registry / "agents.yaml"
    try:
        data = load_yaml(registry_path, auto=auto)
    except ConfigError as exc:
        ui.fail(str(exc))
        return

    agents = data.get("agents") or {}
    if not isinstance(agents, dict) or not agents:
        ui.fail("registry/agents.yaml 未登记任何 Agent")
        return

    linked = 0
    for name, cfg in sorted(agents.items()):
        if not isinstance(cfg, dict):
            continue
        if not cfg.get("enabled"):
            ui.skip(f"{name} 已禁用")
            continue
        if cfg.get("skillMode") != "symlink":
            ui.skip(f"{name} 未声明 skillMode: symlink")
            continue
        _ensure_link(
            paths.agents / name / "skills",
            paths.skills,
            ui,
            label=name,
            force=force,
            check_only=check_only,
        )
        linked += 1

    if linked == 0:
        ui.info("没有 Agent 声明 skillMode: symlink，无需建立联接")


# --------------------------------------------------------------------------
# 入口
# --------------------------------------------------------------------------
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="install.py",
        description="初始化 / 校验 AIHub 环境。默认执行全部步骤，幂等可重复运行。",
        epilog=(
            "步骤 1-3 只依赖标准库；步骤 4、5 需要 PyYAML（读取角色档与 "
            "registry/agents.yaml），仅在真正读到时才请求安装。"
        ),
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="只做只读体检：不创建目录、不写文件、不建联接",
    )
    parser.add_argument(
        "--profile",
        metavar="NAME",
        help="校验 profiles/<NAME>.yaml；这是唯一需要 PyYAML 的步骤",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="重建指向错误的已有联接（真实目录永不删除）",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="自动确认依赖安装，供 CI / 无人值守使用",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdio()
    args = _build_parser().parse_args(argv)
    ui = UI()

    paths, warnings = env.load()

    mode = "只读体检" if args.check_only else "初始化 / 修复"
    print(f"AIHub {mode}")

    step_environment(paths, ui, warnings)
    step_skeleton(paths, ui, check_only=args.check_only)
    step_configs(paths, ui, check_only=args.check_only)

    if args.profile:
        step_profile(paths, ui, args.profile, auto=args.yes)
    else:
        ui.head("4/5  角色档")
        ui.skip("未指定 --profile，跳过校验（该步骤是唯一需要 PyYAML 的地方）")

    step_links(paths, ui, force=args.force, check_only=args.check_only, auto=args.yes)

    print()
    if ui.failures:
        print(f"存在 {len(ui.failures)} 项失败，{len(ui.warnings)} 项告警")
        return 1
    if ui.warnings:
        print(f"完成，{len(ui.warnings)} 项告警（不阻断使用）")
    else:
        print("完成，未发现问题")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
