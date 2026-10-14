#!/usr/bin/env python3
"""Build deterministic GitHub and SkillHub packages for ChengziCV."""

from __future__ import annotations

import argparse
import base64
import hashlib
from html.parser import HTMLParser
import re
import shutil
import sys
import zipfile
from pathlib import Path
from urllib.parse import quote, urlsplit


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
GITHUB_URL = "https://github.com/chengzicv/chengzicv-career-skills"
SKILLHUB_URL = "https://skillhub.cn/skills/user_1f99808e/chengzicv-career-skills"
SKILLHUB_LOGO = "assets/chengzicv-logo-skillhub.svg"
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
    "workspace/README.md",
)
PUBLIC_SKILLS = (
    ("01-必装入口", "chengzicv"),
    ("01-必装入口", "chengzicv-update"),
    ("02-求职建档", "chengzicv-profile"),
    ("03-职业方向", "chengzicv-career"),
    ("04-简历与投递", "chengzicv-resume"),
    ("04-简历与投递", "chengzicv-job-greeting"),
    ("05-面试前准备", "chengzicv-interview-prep"),
    ("05-面试前准备", "chengzicv-interview-script"),
    ("06-面试训练与复盘", "chengzicv-interview-practice"),
    ("06-面试训练与复盘", "chengzicv-interview-mock"),
    ("06-面试训练与复盘", "chengzicv-interview-review"),
    ("07-岗位案例", "chengzicv-case-factory"),
)
SOURCE_SKILLS = {
    "chengzicv-resume": "chengzicv-resume-latest",
    "chengzicv-case-factory": "chengzicv-case-factory-latest",
}
INTERNAL_SKILLS = ("chengzicv-light-business-intake",)
README_CAPABILITY_HEADING = "Skills 里具体有什么东西？"
README_START_HEADING = "安装后怎么开始？"
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
    source_name = SOURCE_SKILLS.get(skill_name, skill_name)
    skill_dir = SKILLS_ROOT / source_name
    # Exported public repositories already use the stable public names.
    if not skill_dir.is_dir():
        skill_dir = SKILLS_ROOT / skill_name
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        raise ValueError(f"missing {skill_name}/SKILL.md")
    text = skill_file.read_text(encoding="utf-8")
    match = re.search(r"^name:\s*([^\n]+)$", text, re.MULTILINE)
    if not match or match.group(1).strip() != skill_dir.name:
        raise ValueError(f"frontmatter name does not match directory: {skill_name}")
    return skill_dir


def public_runtime_bytes(path: Path) -> bytes:
    """Translate local latest identifiers to the stable public invocation names."""
    data = path.read_bytes()
    if path.suffix.lower() not in {".md", ".yaml", ".yml", ".json", ".py", ".txt", ".toml"}:
        return data
    text = data.decode("utf-8")
    for public_name, source_name in SOURCE_SKILLS.items():
        text = text.replace(source_name, public_name)
    return text.encode("utf-8")




def skillhub_source() -> tuple[str, str]:
    source = validate_skill("chengzicv") / "SKILL.md"
    text = public_runtime_bytes(source).decode("utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise ValueError("chengzicv/SKILL.md has no valid frontmatter")
    return match.group(1), text[match.end():].replace("../chengzicv-", "skills/chengzicv-")


def readme_section(readme: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)", readme, re.MULTILINE | re.DOTALL)
    if not match:
        raise ValueError(f"README is missing required section: {heading}")
    return match.group(1).strip()


class ReadmeLogo(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.source = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "img" and attributes.get("alt") == "橙子简历":
            self.source = attributes.get("src") or ""


def readme_logo_path(readme: str) -> Path:
    logo = ReadmeLogo()
    logo.feed(readme)
    logo_path = Path(logo.source)
    if (
        not logo.source or urlsplit(logo.source).scheme or logo_path.is_absolute()
        or ".." in logo_path.parts or not logo_path.parts or logo_path.parts[0] != "assets"
        or not (PACKAGE_ROOT / logo_path).is_file()
    ):
        raise ValueError("README logo must point to an existing repository asset")
    if logo_path.suffix.lower() != ".webp":
        raise ValueError("README logo must be a WebP asset")
    return logo_path


def render_skillhub_logo() -> str:
    """Keep the original artwork intact; size its SVG viewport for Markdown renderers."""
    readme = (PACKAGE_ROOT / "README.md").read_text(encoding="utf-8")
    source = PACKAGE_ROOT / readme_logo_path(readme)
    encoded = base64.b64encode(source.read_bytes()).decode("ascii")
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="280" height="88" viewBox="0 0 280 88">\n'
        '<!-- Generated from the README logo; original WebP bytes are unchanged. -->\n'
        f'<image width="280" height="88" preserveAspectRatio="xMidYMid meet" href="data:image/webp;base64,{encoded}"/>\n'
        '</svg>\n'
    )


def github_absolute_links(text: str) -> str:
    """把仓库内的相对链接换成 GitHub 绝对地址。

    SkillHub 包内只有运行文件，没有 CHANGELOG.md / LICENSE，相对链接在那边是断的。
    """

    def replace(match: re.Match[str]) -> str:
        label, target = match.group(1), match.group(2).strip()
        if urlsplit(target).scheme or target.startswith(("#", "/")):
            return match.group(0)
        return f"[{label}]({GITHUB_URL}/blob/main/{target})"

    return re.sub(r"\[([^\]]*)\]\(([^)]+)\)", replace, text)


def render_skillhub_overview(version: str) -> str:
    """把 README 正文整份搬到 SkillHub，只做平台必需的适配。

    适配只有三处：hero 区（含 HTML）换成带版本号的 logo、仓库内相对链接改成 GitHub 绝对地址、
    结尾保留平台要求的 AI 执行入口。其余文字与仓库 README 逐字一致。
    """
    readme = (PACKAGE_ROOT / "README.md").read_text(encoding="utf-8")
    heading = re.search(r"^# (.+)$", readme, re.MULTILINE)
    if not heading:
        raise ValueError("README has no project introduction")
    readme_logo_path(readme)
    logo_url = f"https://raw.githubusercontent.com/chengzicv/chengzicv-career-skills/v{version}/{quote(SKILLHUB_LOGO)}"

    # 这两处校验与文案搬运无关，但必须继续生效：能力表要列全 12 个公开入口，引导语章节不能丢。
    capabilities = readme_section(readme, README_CAPABILITY_HEADING)
    table = "\n".join(line for line in capabilities.splitlines() if line.startswith("|"))
    actual_skills = re.findall(r"^\|\s*`/([a-z0-9-]+)`\s*\|", table, re.MULTILINE)
    expected_skills = {name for _, name in PUBLIC_SKILLS}
    if len(actual_skills) != len(expected_skills) or set(actual_skills) != expected_skills:
        raise ValueError("README capability table does not match the public Skill list")
    examples = readme_section(readme, README_START_HEADING)
    if not re.search(r"```text\n(.*?)\n```", examples, re.DOTALL):
        raise ValueError("README has no getting-started prompt")

    body = github_absolute_links(readme[heading.end():].strip())
    return f"""# {heading.group(1).strip()}

[![橙子简历]({logo_url})](https://chengzicv.com)

[SkillHub 国内加速安装]({SKILLHUB_URL}) · [GitHub 源码与说明]({GITHUB_URL})

{body}

## AI 执行入口

处理求职请求前，先完整读取并遵循 [执行流程](WORKFLOW.md)，再按其中规则选择子 Skill 并继续任务。本页是使用介绍，不替代执行流程及其配套规则。
"""


def render_skillhub_workflow() -> bytes:
    return skillhub_source()[1].encode("utf-8")


def render_skillhub_root(version: str) -> bytes:
    source_frontmatter, _ = skillhub_source()

    platform_keys = {"slug", "version", "displayName", "summary", "license", "homepage"}
    frontmatter = []
    for line in source_frontmatter.splitlines():
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
    return ("---\n" + "\n".join(frontmatter) + "\n---\n\n" + render_skillhub_overview(version)).encode("utf-8")


def build_github_bundle(version: str) -> Path:
    asset = GITHUB_OUTPUT / GITHUB_ASSET_NAME
    with zipfile.ZipFile(asset, "w") as archive:
        root = "chengzicv-career-skills"
        for _, skill_name in PUBLIC_SKILLS:
            skill_dir = validate_skill(skill_name)
            for path in iter_runtime_files(skill_dir):
                relative = path.relative_to(skill_dir).as_posix()
                add_bytes(archive, f"{root}/{skill_name}/{relative}", public_runtime_bytes(path))

    digest = hashlib.sha256(asset.read_bytes()).hexdigest()
    checksum = asset.with_suffix(asset.suffix + ".sha256")
    checksum.write_text(f"{digest}  {asset.name}\n", encoding="utf-8")
    return asset


def build_skillhub_bundle(version: str) -> Path:
    asset = SKILLHUB_OUTPUT / f"chengzicv-career-skills-{version}.zip"
    root_dir = validate_skill("chengzicv")
    with zipfile.ZipFile(asset, "w") as archive:
        add_bytes(archive, "SKILL.md", render_skillhub_root(version))
        add_bytes(archive, "WORKFLOW.md", render_skillhub_workflow())
        for path in iter_runtime_files(root_dir):
            if path.name != "SKILL.md":
                add_bytes(archive, path.relative_to(root_dir).as_posix(), public_runtime_bytes(path))

        for _, skill_name in PUBLIC_SKILLS:
            if skill_name == "chengzicv":
                continue
            skill_dir = validate_skill(skill_name)
            for path in iter_runtime_files(skill_dir):
                relative = path.relative_to(skill_dir).as_posix()
                add_bytes(archive, f"skills/{skill_name}/{relative}", public_runtime_bytes(path))

    return asset


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-assets", action="store_true", help="regenerate the sized SVG wrapper without building ZIPs")
    args = parser.parse_args()
    if args.prepare_assets:
        (PACKAGE_ROOT / SKILLHUB_LOGO).write_text(render_skillhub_logo(), encoding="utf-8")
        print(f"Prepared {SKILLHUB_LOGO}; include it in the release commit")
        return 0
    if (PACKAGE_ROOT / SKILLHUB_LOGO).read_text(encoding="utf-8") != render_skillhub_logo():
        raise ValueError("SkillHub logo is stale; run tools/build_release.py --prepare-assets and include it in the commit")
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
