#!/usr/bin/env python3
"""fix-eol.py — 统一工作区文本文件的换行符，消除 git 的 CRLF 告警。

问题现象
    git add 时逐文件刷屏：
        warning: in the working copy of 'agents/claude/mappings.yaml',
                 CRLF will be replaced by LF the next time Git touches it

    这不是错误，但有两个实际危害：
      1. 它会把真正的告警（引用失效、体积超预算）淹掉；
      2. 索引里存的是 CRLF、工作区也是 CRLF，而 .gitattributes 要求 LF，
         于是「git 下次碰它」时会整文件重写 —— 产生与内容无关的巨大 diff。

解决思路
    .gitattributes 声明了 `* text=auto eol=lf`，即仓库与工作区都用 LF。
    所以只要把工作区的 CRLF 文本文件就地改成 LF，告警自然消失，
    且索引与工作区从此一致。

本脚本的边界
    · 二进制（前 8KB 含 NUL）一律跳过，绝不改写。
    · Windows 原生脚本保持 CRLF —— 具体是哪些扩展名，直接从
      .gitattributes 里读 `eol=crlf` 规则，不在本文件里另抄一份，
      避免策略两处维护后漂移。
    · 默认只报告、不动文件；要改写必须显式加 --write。
    · 只处理 git 认识的路径（已跟踪 + 未跟踪但未被 .gitignore 排除），
      因此 agents/<name>/skills 这类运行时目录联接天然不会被碰到。

用法
    python3 scripts/fix-eol.py                       # 体检：列出所有不符合策略的文件
    python3 scripts/fix-eol.py --write               # 就地规范化
    python3 scripts/fix-eol.py --write --backup D:/bak   # 改写前先按原路径备份

退出码
    0  无需处理，或已全部处理完成
    1  体检模式下发现了不符合策略的文件（可用于 pre-commit / CI 阻断）
"""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

# 兜底值：只有当 .gitattributes 缺失或读不出 eol=crlf 规则时才使用
DEFAULT_CRLF_SUFFIXES = frozenset({".bat", ".cmd", ".ps1", ".psm1", ".psd1"})

NUL_SCAN_BYTES = 8192


# --------------------------------------------------------------------------
# 换行符识别与转换
# --------------------------------------------------------------------------
def classify(data: bytes) -> str:
    """返回文件的换行符风格：binary / no-EOL / LF / CRLF / MIXED / CR-only。"""
    if b"\0" in data[:NUL_SCAN_BYTES]:
        return "binary"

    has_crlf = b"\r\n" in data
    remainder = data.replace(b"\r\n", b"")          # 去掉成对 CRLF 后
    has_lone_lf = b"\n" in remainder
    has_lone_cr = b"\r" in remainder

    if has_crlf and (has_lone_lf or has_lone_cr):
        return "MIXED"
    if has_crlf:
        return "CRLF"
    if has_lone_lf:
        return "LF"
    if has_lone_cr:
        return "CR-only"
    return "no-EOL"


def to_lf(data: bytes) -> bytes:
    """CRLF 与孤立 CR 一律折成 LF。"""
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def to_crlf(data: bytes) -> bytes:
    """先折成 LF 再统一展开，避免出现 CRCRLF。"""
    return to_lf(data).replace(b"\n", b"\r\n")


def normalize(data: bytes, *, target: str) -> bytes:
    return to_crlf(data) if target == "crlf" else to_lf(data)


# --------------------------------------------------------------------------
# 策略来源：.gitattributes
# --------------------------------------------------------------------------
def crlf_suffixes(root: Path) -> frozenset[str]:
    """从 .gitattributes 提取所有声明了 eol=crlf 的简单扩展名。

    只认 `*.ext ... eol=crlf` 这种单层通配，复杂模式（含 * ? [ ]）忽略 ——
    本仓库的策略就是「按扩展名区分」，把解析范围收紧反而更不容易出错。
    """
    found: set[str] = set()
    spec = root / ".gitattributes"
    if not spec.is_file():
        return DEFAULT_CRLF_SUFFIXES

    try:
        text = spec.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return DEFAULT_CRLF_SUFFIXES

    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        fields = line.split()
        if len(fields) < 2 or fields[0].startswith("!"):
            continue
        if "eol=crlf" not in fields[1:]:
            continue
        pattern = fields[0]
        if pattern.startswith("*.") and not any(c in pattern[2:] for c in "*?[]"):
            found.add("." + pattern[2:].lower())

    return frozenset(found) or DEFAULT_CRLF_SUFFIXES


# --------------------------------------------------------------------------
# 文件枚举
# --------------------------------------------------------------------------
def _via_link(root: Path, path: Path) -> bool:
    """判断路径是否穿过目录联接 / 符号链接。

    Windows 的 junction 不算 symlink（Path.is_symlink() 为 False），
    只能看 reparse 属性 —— 与 scripts/install.py 的判断保持一致。
    """
    try:
        parts = path.relative_to(root).parts[:-1]
    except ValueError:
        return False

    current = root
    for part in parts:
        current = current / part
        try:
            st = os.lstat(current)
        except OSError:
            return False
        if stat.S_ISLNK(st.st_mode) or getattr(st, "st_reparse_tag", 0):
            return True
    return False


def git_paths(root: Path) -> list[Path]:
    """列出 git 认识的库内文件：已跟踪 + 未跟踪但未被忽略。"""
    try:
        proc = subprocess.run(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            cwd=root,
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"  [FAIL] 无法列出 git 文件：{exc}", file=sys.stderr)
        return []

    names = proc.stdout.decode("utf-8", "surrogateescape").split("\0")

    # 按真实路径去重：目录联接（agents/claude/skills → shared/skills）
    # 会让同一份物理文件以多个路径出现，重复处理没有意义还会重复报告。
    # 同一份文件只保留「不经联接」的那个路径，否则报告会指向 shared/ 之外的别名。
    candidates = sorted(
        (root / name for name in names if name),
        key=lambda p: (_via_link(root, p), str(p)),
    )

    seen: set[str] = set()
    result: list[Path] = []
    for path in candidates:
        if not path.is_file():
            continue
        try:
            key = str(path.resolve())
        except OSError:
            key = str(path)
        if key in seen:
            continue
        seen.add(key)
        result.append(path)
    return result


# --------------------------------------------------------------------------
# 原子写入
# --------------------------------------------------------------------------
def _atomic_write(root: Path, target: Path, data: bytes) -> None:
    """先写临时文件再整体替换，避免中途失败留下半个文件。

    临时文件优先落在 runtime/tmp/ —— AGENTS.md §1.7 要求仓库内生成物只写
    runtime/，且它与目标同处一个卷（os.replace 跨卷会失败）。
    若 runtime/tmp 不可用，退回与目标同目录的临时文件。
    """
    candidates = [root / "runtime" / "tmp" / (target.name + ".eoltmp")]
    candidates.append(target.with_name(target.name + ".eoltmp"))

    last_error: OSError | None = None
    for tmp in candidates:
        try:
            tmp.parent.mkdir(parents=True, exist_ok=True)
            tmp.write_bytes(data)
            shutil.copymode(target, tmp)
            tmp.replace(target)
            return
        except OSError as exc:
            last_error = exc
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass

    raise last_error or OSError(f"无法写入 {target}")


# --------------------------------------------------------------------------
# 主流程
# --------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="fix-eol.py",
        description="按 .gitattributes 的策略统一工作区换行符，消除 git 的 CRLF 告警。",
        epilog="默认只报告；要改写请加 --write。",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="真正改写文件（默认只做只读体检）",
    )
    parser.add_argument(
        "--backup",
        metavar="DIR",
        help="改写前把原始文件按相对路径复制到 DIR",
    )
    parser.add_argument(
        "--repo",
        metavar="PATH",
        help="仓库根目录，默认自动探测（git rev-parse --show-toplevel）",
    )
    args = parser.parse_args(argv)

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8")
            except (OSError, ValueError):
                pass

    root = _resolve_root(args.repo)
    if root is None:
        print("  [FAIL] 找不到仓库根目录，请用 --repo 指定", file=sys.stderr)
        return 1

    crlf_ext = crlf_suffixes(root)
    backup_root = Path(args.backup).expanduser().resolve() if args.backup else None
    if backup_root is not None and not args.write:
        print("  [WARN] 只给了 --backup 却没给 --write，不会产生任何备份")

    mode = "改写" if args.write else "只读体检"
    print(f"fix-eol  {mode}   {root}")
    print(f"         CRLF 例外扩展名：{', '.join(sorted(crlf_ext))}")

    paths = git_paths(root)
    if not paths:
        print("  [FAIL] 没有可处理的文件")
        return 1

    offenders: list[tuple[Path, str, str, bytes]] = []
    stats: dict[str, int] = {}

    for path in paths:
        try:
            data = path.read_bytes()
        except OSError as exc:
            print(f"  [WARN] 读取失败：{path.relative_to(root)}  {exc}")
            continue

        kind = classify(data)
        stats[kind] = stats.get(kind, 0) + 1
        if kind in ("binary", "no-EOL"):
            continue

        target = "crlf" if path.suffix.lower() in crlf_ext else "lf"
        fixed = normalize(data, target=target)
        if fixed != data:
            offenders.append((path, kind, target, data))

    print()
    total = len(paths)
    parts = "  ".join(f"{k}={v}" for k, v in sorted(stats.items()))
    print(f"         扫描 {total} 个文件    {parts}")
    print()

    if not offenders:
        print("  [OK  ] 全部文本文件已符合策略，无需处理")
        return 0

    print(f"         发现 {len(offenders)} 个文件不符合策略：")
    for path, kind, target, _ in offenders:
        rel = path.relative_to(root).as_posix()
        print(f"         [{kind:<7}→{target.upper():<4}] {rel}")
    print()

    if not args.write:
        print(f"  [INFO] 未做任何改动。执行 `python3 scripts/fix-eol.py --write` 修复")
        print(f"  [INFO] 修复后请运行 `git add --renormalize .` 让索引同步为 LF")
        return 1

    written = 0
    for path, _, target, original in offenders:
        rel = path.relative_to(root).as_posix()
        if backup_root is not None:
            try:
                dest = backup_root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(original)
            except OSError as exc:
                print(f"  [FAIL] 备份 {rel} 失败，已跳过改写：{exc}")
                continue

        try:
            fixed = normalize(original, target=target)
            _atomic_write(root, path, fixed)
        except OSError as exc:
            print(f"  [FAIL] 改写 {rel} 失败：{exc}")
            continue
        written += 1

    print(f"  [OK  ] 已改写 {written}/{len(offenders)} 个文件为 LF/CRLF")
    if backup_root is not None:
        print(f"         原始副本：{backup_root}")
    print("  [NEXT] git add --renormalize .")
    return 0 if written == len(offenders) else 1


def _resolve_root(explicit: str | None) -> Path | None:
    if explicit:
        path = Path(explicit).expanduser().resolve()
        return path if path.is_dir() else None

    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(proc.stdout.strip()).resolve()
    except (OSError, subprocess.CalledProcessError):
        pass

    # git 不可用时的兜底：本文件位于 <root>/scripts/ 下
    guess = Path(__file__).resolve().parent.parent
    return guess if (guess / ".gitattributes").is_file() else None


if __name__ == "__main__":
    raise SystemExit(main())
