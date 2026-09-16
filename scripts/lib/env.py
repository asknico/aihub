"""env.py — 环境变量加载与路径派生。

设计要点
    1. **只读文件，不要求变量已在系统环境里。**
       `os.environ["AIHUB_HOME"]` 在没 export 过的机器上直接 KeyError；
       而 .env 存在的意义恰恰是「不污染系统环境」。
    2. **AIHUB_SKILLS 优先读 .env，缺失时从 AIHUB_HOME 派生。**
       它是 HOME + 固定后缀的纯派生值，独立维护会造出第二份事实源；
       但 AGENTS.md §6 把它列为环境变量，故取折中：以派生值为准，
       发现 .env 里的值与推导结果不一致时给出告警而不静默采纳。
    3. **本模块不打印任何东西。** 由调用方决定如何呈现，
       以免同一个告警在多个脚本里被重复输出。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# scripts/lib/env.py -> scripts -> <repo root>
REPO_ROOT = Path(__file__).resolve().parents[2]

# AGENTS.md §6 写的是 env/.env，但实际值常被放在仓库根。两者都认。
ENV_CANDIDATES = ("env/.env", ".env")


def parse_dotenv(text: str) -> dict[str, str]:
    """解析 .env 文本。

    刻意只支持最小子集：空行、# 注释、KEY=VALUE、引号包裹的值。
    **不支持 ${VAR} 插值** —— 同一份 .env 在不同读取工具下插值行为不一致
    （python-dotenv 会展开、shell 的 source 视变量是否已存在、PowerShell
    自写解析则原样保留字面量），依赖它会让脚本在某个平台上静默拿到空值。
    所有派生值一律在 Python 里算。
    """
    result: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # 去掉成对的引号，但不要破坏不成对的值
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key:
            result[key] = value
    return result


@dataclass(frozen=True)
class Paths:
    """AIHub 的路径集合。

    一次性算好、全项目只认这一份，避免「每个脚本各自拼一遍路径」。
    frozen 是刻意的：路径在运行期不应被改写。
    """

    root: Path
    skills: Path
    rules: Path
    knowledge: Path
    prompts: Path
    templates: Path
    agents: Path
    mcp: Path
    profiles: Path
    registry: Path
    script_dir: Path
    runtime: Path
    data: Path
    env_file: Path | None

    @property
    def env_example(self) -> Path:
        return self.root / ".env.example"


def load(root: Path | None = None) -> tuple[Paths, list[str]]:
    """定位 .env、解析变量、派生全部路径。

    返回 (Paths, 告警列表)。告警不阻断执行 —— 它们描述的是
    「配置与实际情况有出入」，由调用方决定是否展示。
    """
    root = (root or REPO_ROOT).resolve()
    warnings: list[str] = []

    env_file = next((root / c for c in ENV_CANDIDATES if (root / c).is_file()), None)
    values: dict[str, str] = {}
    if env_file is not None:
        values = parse_dotenv(env_file.read_text(encoding="utf-8"))

    # --- AIHUB_HOME：.env 优先，其次「本文件所在仓库」 ---
    declared_home = values.get("AIHUB_HOME", "").strip()
    if declared_home:
        home = Path(declared_home)
        if home.resolve() != root:
            warnings.append(
                f"AIHUB_HOME 指向 {home}，但本脚本所在仓库是 {root}。"
                "若仓库已迁移，请同步更新 .env。"
            )
    else:
        home = root
        label = env_file.name if env_file else ".env"
        warnings.append(f"{label} 未定义 AIHUB_HOME，已回退为仓库位置 {root}")

    # --- AIHUB_SKILLS：派生值为准，声明值不一致则告警 ---
    skills = home / "shared" / "skills"
    declared_skills = values.get("AIHUB_SKILLS", "").strip()
    if declared_skills and Path(declared_skills).resolve() != skills.resolve():
        warnings.append(
            f"AIHUB_SKILLS={declared_skills} 与派生值 {skills} 不一致；"
            "以派生值为准（AIHUB_SKILLS = AIHUB_HOME/shared/skills）"
        )

    # --- AIHUB_DATA：在仓库之外，无法推导，必须独立定义 ---
    declared_data = values.get("AIHUB_DATA", "").strip()
    if declared_data:
        data = Path(declared_data)
    else:
        data = home.parent / "AIHub_Data"
        warnings.append(f".env 未定义 AIHUB_DATA，已回退为 {data}")

    return (
        Paths(
            root=home,
            skills=skills,
            rules=home / "shared" / "rules",
            knowledge=home / "shared" / "knowledge",
            prompts=home / "shared" / "prompts",
            templates=home / "templates",
            agents=home / "agents",
            mcp=home / "mcp",
            profiles=home / "profiles",
            registry=home / "registry",
            script_dir=home / "scripts",
            runtime=home / "runtime",
            data=data,
            env_file=env_file,
        ),
        warnings,
    )
