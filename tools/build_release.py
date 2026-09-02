#!/usr/bin/env python3
"""Build deterministic GitHub and SkillHub packages for ChengziCV."""

from __future__ import annotations

import hashlib
import re
import shutil
import sys
import zipfile
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = (
    PACKAGE_ROOT
    if (PACKAGE_ROOT / "chengzicv" / "SKILL.md").is_file()
    else PACKAGE_ROOT.parent
)
OUTPUT = PACKAGE_ROOT / "dist"
GITHUB_OUTPUT = OUTPUT / "skills"
SKILLHUB_OUTPUT = OUTPUT / "skillhub"
GITHUB_ASSET_NAME = "chengzicv-career-skills.zip"
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
    "strategy.json",
)
PUBLIC_SKILLS = (
    ("01-必装入口", "chengzicv"),
    ("01-必装入口", "chengzicv-update"),
    ("02-求职建档", "chengzicv-profile"),
    ("03-职业方向", "chengzicv-career"),
    ("04-简历与投递", "chengzicv-resume"),
    ("04-简历与投递", "chengzicv-job-greeting"),
    ("05-面试前准备", "chengzicv-interview-prep"),
    ("06-面试训练与复盘", "chengzicv-interview-practice"),
    ("06-面试训练与复盘", "chengzicv-interview-mock"),
    ("06-面试训练与复盘", "chengzicv-interview-review"),
    ("07-岗位案例", "chengzicv-case-factory"),
)
INTERNAL_SKILLS = ("chengzicv-light-business-intake",)
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
                relative_parts = path.relative_to(skill_dir).parts
                if path.is_file() and not any(
                    part == "__pycache__" or part.startswith(".")
                    for part in relative_parts
                ):
                    yield path


def read_version() -> str:
    version = (PACKAGE_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError(f"invalid VERSION: {version!r}")
    return version


def validate_skill(skill_name: str) -> Path:
    skill_dir = SKILLS_ROOT / skill_name
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


def github_bundle_readme(version: str) -> str:
    return f"""# ChengziCV Career Skills v{version}

这是给不使用命令行的用户准备的安装包，包含 1 个求职导航入口、9 个求职执行 Skill 和 1 个更新入口。

## WorkBuddy 等客户端导入方法

1. 解压当前安装包。
2. 打开客户端的 Skills 管理页面，选择导入或安装本地 Skill。
3. 按需要导入分类目录中的 ZIP；每个 ZIP 都是一个可独立导入的 Skill。
4. 不知道从哪里开始时，至少导入 `01-必装入口/chengzicv.zip`，然后直接说：“用 ChengziCV 帮我判断现在最该先处理哪个求职问题。”
5. 希望以后直接说“更新 ChengziCV Skills”时，同时导入 `chengzicv-update.zip`。客户端不能执行终端命令时，仍需重新下载新版安装包。

项目主页：https://github.com/chengzicv/chengzicv-career-skills
官网：https://chengzicv.com
"""


def render_skillhub_root(version: str) -> bytes:
    source = validate_skill("chengzicv") / "SKILL.md"
    text = source.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise ValueError("chengzicv/SKILL.md has no valid frontmatter")

    platform_keys = {"slug", "version", "displayName", "summary", "license", "homepage"}
    frontmatter = []
    for line in match.group(1).splitlines():
        key = line.split(":", 1)[0].strip()
        if key not in platform_keys:
            frontmatter.append(line)
    frontmatter.extend(
        (
            "slug: chengzicv-career-skills",
            f"version: {version}",
            'displayName: "ChengziCV 全链路求职 Skills"',
            'summary: "橙子简历完整求职套件：建档、职业规划、简历优化、招聘平台沟通、面试准备与复盘"',
            "license: MIT",
            "homepage: https://github.com/chengzicv/chengzicv-career-skills",
        )
    )
    body = text[match.end():].replace("../chengzicv-", "skills/chengzicv-")
    return ("---\n" + "\n".join(frontmatter) + "\n---\n" + body).encode("utf-8")


def build_github_bundle(version: str) -> Path:
    staging = GITHUB_OUTPUT / "bundle"
    staging.mkdir(parents=True)
    (staging / "README.md").write_text(github_bundle_readme(version), encoding="utf-8")

    for group, skill_name in PUBLIC_SKILLS:
        group_dir = staging / group
        group_dir.mkdir(exist_ok=True)
        build_skill_zip(skill_name, group_dir / f"{skill_name}.zip")

    asset = GITHUB_OUTPUT / GITHUB_ASSET_NAME
    with zipfile.ZipFile(asset, "w") as archive:
        for path in sorted(staging.rglob("*")):
            if path.is_file():
                add_bytes(archive, path.relative_to(staging).as_posix(), path.read_bytes())

    digest = hashlib.sha256(asset.read_bytes()).hexdigest()
    checksum = asset.with_suffix(asset.suffix + ".sha256")
    checksum.write_text(f"{digest}  {asset.name}\n", encoding="utf-8")
    return asset


def build_skillhub_bundle(version: str) -> Path:
    asset = SKILLHUB_OUTPUT / f"chengzicv-career-skills-{version}.zip"
    root_dir = validate_skill("chengzicv")
    with zipfile.ZipFile(asset, "w") as archive:
        add_bytes(archive, "SKILL.md", render_skillhub_root(version))
        for path in iter_runtime_files(root_dir):
            if path.name != "SKILL.md":
                add_bytes(archive, path.relative_to(root_dir).as_posix(), path.read_bytes())

        for _, skill_name in PUBLIC_SKILLS:
            if skill_name == "chengzicv":
                continue
            skill_dir = validate_skill(skill_name)
            for path in iter_runtime_files(skill_dir):
                relative = path.relative_to(skill_dir).as_posix()
                add_bytes(archive, f"skills/{skill_name}/{relative}", path.read_bytes())

    return asset


def main() -> int:
    version = read_version()
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    GITHUB_OUTPUT.mkdir(parents=True)
    SKILLHUB_OUTPUT.mkdir(parents=True)

    for internal in INTERNAL_SKILLS:
        if internal in {name for _, name in PUBLIC_SKILLS}:
            raise ValueError(f"internal Skill leaked into public list: {internal}")

    github_asset = build_github_bundle(version)
    skillhub_asset = build_skillhub_bundle(version)
    print(f"Built {github_asset.relative_to(PACKAGE_ROOT)}")
    print(f"Built {skillhub_asset.relative_to(PACKAGE_ROOT)}")
    print(f"Packaged {len(PUBLIC_SKILLS)} public ChengziCV components for v{version}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
