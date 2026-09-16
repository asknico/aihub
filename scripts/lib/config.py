"""config.py — YAML 配置读取的统一入口。

**本模块是全项目唯一 import yaml 的地方。**
其余脚本一律通过 load_yaml() 读配置，好处有三：
    - 依赖检查只在一处，不会出现某个脚本漏检；
    - 将来换库（例如改用 ruamel.yaml 以保留注释）只改这一个文件；
    - 不读 YAML 的脚本永远不会被要求安装 PyYAML。

错误处理原则
    本模块抛出 ConfigError 而不调用 sys.exit()：库不应该决定进程的生死，
    退出方式由入口脚本决定。反过来，入口脚本必须捕获它并给出非零退出码。
"""

from __future__ import annotations

from pathlib import Path

from lib.deps import ensure


class ConfigError(Exception):
    """配置文件不可用（缺失 / 格式错误 / 结构不符）。"""


def load_yaml(path: Path, *, auto: bool = False) -> dict:
    """读取 YAML 配置。

    首次真正调用时才确保 PyYAML 可用 —— 延迟到这一刻，
    是为了让「只做目录检查」的运行路径完全零依赖。

    auto=True 时跳过安装询问，供 CI / 无人值守场景使用。
    """
    if not ensure("PyYAML", auto=auto):
        raise ConfigError(
            f"缺少 PyYAML，无法读取 {path.name}。\n"
            "  安装后重试，或改用不读配置的子命令（如 --check-only）。"
        )

    import yaml  # 延迟导入：必须放在 ensure() 之后

    if not path.is_file():
        raise ConfigError(f"配置文件不存在：{path}")

    try:
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        # YAML 语法错误必须指到文件，否则排查时不知道是哪个 profile 的问题
        raise ConfigError(f"{path} 语法错误：{exc}") from exc

    if data is None:
        # 空文件或只有注释。返回空映射而不是 None，
        # 让调用方不必到处写 `or {}`。
        return {}

    if not isinstance(data, dict):
        raise ConfigError(
            f"{path} 的顶层结构应为映射，实际是 {type(data).__name__}"
        )

    return data
