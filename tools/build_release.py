#!/usr/bin/env python3
"""Build deterministic ChengziCV Skill archives for GitHub Releases."""

from __future__ import annotations

import re
import shutil
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dist" / "skills"
ASSET_NAME = "chengzicv-career-skills.zip"
RUNTIME_ENTRIES = (
    "SKILL.md",
    "agents",
    "onboarding",
    "references",
    "scripts",
    "schemas",
    "runtime",
    "scorecards",
    "prompts",
    "assets",
)
SKILLS = (
    ("01-必装入口", "chengzicv"),
    ("01-必装入口", "chengzicv-update"),
    ("02-求职建档", "chengzicv-profile"),
    ("03-职业方向", "chengzicv-career"),
    ("04-简历优化", "chengzicv-resume"),
    ("05-面试训练", "chengzicv-interview-practice"),
    ("05-面试训练", "chengzicv-interview-mock"),
    ("05-面试训练", "chengzicv-interview-review"),
)
ZIP_TIME = (2026, 1, 1, 0, 0, 0)


def add_bytes(archive: zipfile.ZipFile, path: str, data: bytes) -> None:
    info = zipfile.ZipInfo(path, ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data)


def iter_runtime_files(skill_dir: Path):
    for entry_name in RUNTIME_ENTRIES:
        entry = skill_dir / entry_name
        if entry.is_file():
            yield entry
        elif entry.is_dir():
            for path in sorted(entry.rglob("*")):
                if path.is_file() and not any(
                    part == "__pycache__" or part.startswith(".")
                    for part in path.relative_to(skill_dir).parts
                ):
                    yield path


def validate_skill(skill_name: str) -> Path:
    skill_dir = ROOT / skill_name
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        raise ValueError(f"missing {skill_name}/SKILL.md")
    text = skill_file.read_text(encoding="utf-8")
    match = re.search(r"^name:\s*([^\n]+)$", text, re.MULTILINE)
    if not match or match.group(1).strip() != skill_name:
        raise ValueError(f"frontmatter name does not match directory: {skill_name}")
    return skill_dir


def build_skill_zip(skill_name: str, target: Path) -> None:
    skill_dir = validate_skill(skill_name)
    with zipfile.ZipFile(target, "w") as archive:
        for path in iter_runtime_files(skill_dir):
            add_bytes(archive, path.relative_to(skill_dir).as_posix(), path.read_bytes())


def package_readme(version: str) -> str:
    return f"""# ChengziCV Career Skills v{version}

这是给不使用命令行的用户准备的安装包，包含 7 个求职 Skills 和 1 个更新入口。

## WorkBuddy 导入方法

1. 解压当前安装包。
2. 打开 WorkBuddy 的 Skills 管理页面，点击“导入 Skill”。
3. 依次导入各分类目录中的 8 个 ZIP；每个 ZIP 就是一个可独立导入的 Skill。
4. 导入后直接说：“用 ChengziCV 帮我判断现在最该先处理哪个求职问题。”

推荐至少导入 `01-必装入口/chengzicv.zip`。如需以后直接说“更新 ChengziCV Skills”，同时导入 `chengzicv-update.zip`；客户端无法执行终端命令时，仍需重新下载此安装包导入。

项目主页：https://github.com/chengzicv/chengzicv-career-skills
官网：https://chengzicv.com
"""


def main() -> int:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError(f"invalid VERSION: {version!r}")

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    staging = OUTPUT / "bundle"
    staging.mkdir(parents=True)
    (staging / "README.md").write_text(package_readme(version), encoding="utf-8")

    for group, skill_name in SKILLS:
        group_dir = staging / group
        group_dir.mkdir(exist_ok=True)
        build_skill_zip(skill_name, group_dir / f"{skill_name}.zip")

    asset = OUTPUT / ASSET_NAME
    with zipfile.ZipFile(asset, "w") as archive:
        for path in sorted(staging.rglob("*")):
            if path.is_file():
                add_bytes(archive, path.relative_to(staging).as_posix(), path.read_bytes())

    print(f"Built {asset.relative_to(ROOT)} with {len(SKILLS)} Skills for v{version}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
