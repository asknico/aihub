"""
deps.py — 第三方依赖的检测与按需安装。

设计前提
    AIHub 脚本默认保持零依赖。「建目录 / 建联接 / 校验引用存在性」这类
    高频操作只用到标准库，新用户 clone 下来即可直接运行。

    只有需要读 YAML 语义的脚本（例如从 profile 生成 registry）才用到
    PyYAML。本模块保证这类脚本在缺依赖时给出**一条可复制的补救命令**，
    而不是甩出一段 traceback。

核心原则
    1. 用 sys.executable，绝不用写死的 "python" / "python3"。
       写死就可能装进别的解释器，导致「装了但 import 不到」。
    2. 默认不静默安装。修改用户环境是需要被告知的动作，
       因此默认交互确认；CI 场景才用 auto=True。
    3. 三个平台、两种环境（全局 / venv）走同一条代码路径，
       平台差异不在这里体现。
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys

# 分发包名 -> 导入名。两者不一致时（PyYAML -> yaml）必须映射，
# 否则检测会误判为「未安装」。
DEPS: dict[str, str] = {
    "PyYAML": "yaml",
}


def in_venv() -> bool:
    """当前解释器是否运行在虚拟环境中。

    venv 里 sys.prefix != sys.base_prefix；全局环境两者相等。
    """
    return sys.prefix != sys.base_prefix


def has(dist_name: str) -> bool:
    """检测依赖是否可用。

    用 find_spec 而非真正 import：既避免导入副作用，也让检测本身
    不依赖被检测的包。注意 find_spec 找不到时返回 None 而不是抛错，
    但父包不存在时抛 ModuleNotFoundError，故包一层。
    """
    import_name = DEPS.get(dist_name, dist_name)
    try:
        return importlib.util.find_spec(import_name) is not None
    except (ImportError, ValueError):
        return False


def install_cmd(dist_name: str) -> list[str]:
    """构造安装命令。

    非 venv 环境加 --user：装到用户目录，不需要管理员 / root 权限，
    也就不会去动系统 Python 的包目录。venv 里 --user 会直接报错
    （"User site-packages are not visible in this virtualenv"），
    所以两种情况必须分开。
    """
    cmd = [sys.executable, "-m", "pip", "install"]
    if not in_venv():
        cmd.append("--user")
    cmd.append(dist_name)
    return cmd


def install(dist_name: str) -> bool:
    """用当前解释器安装依赖，返回是否成功。"""
    cmd = install_cmd(dist_name)
    print("  $ " + " ".join(cmd))

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        _report_failure(proc)
        return False

    _refresh_import_path()
    return True


def _report_failure(proc: subprocess.CompletedProcess) -> None:
    """把 pip 的失败翻译成用户能直接照做的下一步。"""
    output = (proc.stderr or "") + (proc.stdout or "")

    if "externally-managed-environment" in output:
        # PEP 668：Debian 12 / Ubuntu 23.04+ / Homebrew Python 的默认保护
        print("  该 Python 受 PEP 668 保护，不允许直接写入包目录。")
        print("  推荐改用虚拟环境：")
        print(f"    {sys.executable} -m venv .venv")
        print("    然后重新运行本脚本（用 .venv 里的解释器）")
        return

    if "No module named pip" in output:
        print("  当前 Python 没有 pip。请先安装：")
        print(f"    {sys.executable} -m ensurepip --upgrade")
        return

    print("  安装失败，pip 输出：")
    print("  " + output.strip().replace("\n", "\n  "))


def _refresh_import_path() -> None:
    """让新装的包在当前进程内立即可见。

    这一步不是可选的。site 模块在进程启动时就已决定 sys.path，
    而 --user 的包目录（site.getusersitepackages()）在启动时若不存在，
    根本不会被加进去。装完目录有了，sys.path 里仍然没有它 ——
    于是同进程内 find_spec 依然返回 None，表现为「装了却检测不到」。
    所以必须手动补 path 并清掉导入缓存。
    """
    import importlib
    import site

    candidates = [site.getusersitepackages()]
    get_site_packages = getattr(site, "getsitepackages", None)
    if get_site_packages is not None:
        candidates += list(get_site_packages())

    for path in candidates:
        if path and path not in sys.path:
            sys.path.append(path)

    importlib.invalidate_caches()


def ensure(dist_name: str, *, auto: bool = False) -> bool:
    """确保依赖可用，缺失时按需安装。

    auto=False（默认）
        交互确认后安装；用户拒绝则打印手动命令并返回 False。
    auto=True
        直接安装，用于 CI / 无人值守场景。
    """
    if has(dist_name):
        return True

    if not auto:
        try:
            reply = input(f"缺少依赖 {dist_name}，现在安装？[y/N] ").strip().lower()
        except EOFError:
            # 无终端（被重定向 / 在 CI 里跑）时不要卡死
            reply = ""

        if reply not in ("y", "yes"):
            print("  已跳过。需要时请手动执行：")
            print("    " + " ".join(install_cmd(dist_name)))
            return False

    if not install(dist_name):
        return False

    if not has(dist_name):
        print(f"  {dist_name} 安装完成但仍无法导入 ——")
        print("  可能装进了另一个解释器。请检查：")
        print(f"    {sys.executable} -m pip show {dist_name}")
        return False

    return True
