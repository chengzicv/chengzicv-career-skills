#!/usr/bin/env python3
"""Verify ChengziCV GitHub and SkillHub release archives."""

from __future__ import annotations

import posixpath
import re
import sys
import urllib.parse
import zipfile
from pathlib import PurePosixPath

from build_release import (
    GITHUB_ASSET_NAME,
    GITHUB_OUTPUT,
    INTERNAL_SKILLS,
    PACKAGE_ROOT,
    PUBLIC_SKILLS,
    SKILLHUB_OUTPUT,
    iter_runtime_files,
    validate_skill,
    public_runtime_bytes,
    read_version,
    render_skillhub_workflow,
)


FORBIDDEN_PARTS = {".DS_Store", "__pycache__", "candidate-data", "local-data", "outputs"}
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
SKILLHUB_ALLOWED_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".py", ".txt", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".csv", ".toml"}


def fail(message: str) -> None:
    raise ValueError(message)


def validate_names(names: list[str], label: str) -> None:
    for name in names:
        parts = PurePosixPath(name).parts
        if any(part in FORBIDDEN_PARTS or part.startswith(".env") for part in parts):
            fail(f"{label} contains forbidden path: {name}")
        if any(internal in name for internal in INTERNAL_SKILLS):
            fail(f"{label} contains internal Skill: {name}")


def frontmatter_value(text: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*[\"']?([^\n\"']+)", text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def verify_relative_markdown_links(archive: zipfile.ZipFile) -> None:
    names = set(archive.namelist())
    for name in sorted(names):
        if not name.endswith(".md"):
            continue
        text = archive.read(name).decode("utf-8")
        for raw_target in MARKDOWN_LINK.findall(text):
            target = raw_target.strip().strip("<>")
            parsed = urllib.parse.urlsplit(target)
            if parsed.scheme or target.startswith(("#", "/")):
                continue
            path = urllib.parse.unquote(parsed.path)
            if not path or any(marker in path for marker in ("{", "}", "<", ">")):
                continue
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), path))
            if resolved.startswith("../") or resolved not in names:
                fail(f"broken relative Markdown link in {name}: {raw_target}")


def verify_github_bundle() -> None:
    asset = GITHUB_OUTPUT / GITHUB_ASSET_NAME
    if not asset.is_file():
        fail(f"missing GitHub bundle: {asset}")
    with zipfile.ZipFile(asset) as outer:
        names = outer.namelist()
        validate_names(names, "GitHub bundle")
        root = "chengzicv-career-skills"
        expected: set[str] = set()
        for _, skill_name in PUBLIC_SKILLS:
            skill_dir = validate_skill(skill_name)
            expected.update(
                f"{root}/{skill_name}/{path.relative_to(skill_dir).as_posix()}"
                for path in iter_runtime_files(skill_dir)
            )
        if set(names) != expected:
            fail(f"GitHub bundle entries differ: expected={sorted(expected)} actual={sorted(names)}")

        nested_archives = [name for name in names if name.lower().endswith(".zip")]
        if nested_archives:
            fail(f"GitHub bundle contains nested ZIP files: {nested_archives}")

        for _, skill_name in PUBLIC_SKILLS:
            skill_file = f"{root}/{skill_name}/SKILL.md"
            agent_file = f"{root}/{skill_name}/agents/openai.yaml"
            if skill_file not in names:
                fail(f"GitHub bundle is missing {skill_file}")
            if agent_file not in names:
                fail(f"GitHub bundle is missing {agent_file}")
            skill_text = outer.read(skill_file).decode("utf-8")
            if frontmatter_value(skill_text, "name") != skill_name:
                fail(f"{skill_file} frontmatter name mismatch")

        verify_relative_markdown_links(outer)


def verify_skillhub_bundle(version: str) -> None:
    asset = SKILLHUB_OUTPUT / f"chengzicv-career-skills-{version}.zip"
    if not asset.is_file():
        fail(f"missing SkillHub bundle: {asset}")
    with zipfile.ZipFile(asset) as archive:
        names = archive.namelist()
        validate_names(names, "SkillHub bundle")
        required = {"SKILL.md", "WORKFLOW.md", "agents/openai.yaml"}
        required.update(
            f"skills/{skill_name}/SKILL.md"
            for _, skill_name in PUBLIC_SKILLS
            if skill_name != "chengzicv"
        )
        missing = sorted(required - set(names))
        if missing:
            fail(f"SkillHub bundle is missing: {missing}")
        unsupported = sorted(
            name for name in names if PurePosixPath(name).suffix.lower() not in SKILLHUB_ALLOWED_SUFFIXES
        )
        if unsupported:
            fail(f"SkillHub bundle contains unsupported file types: {unsupported}")

        root_text = archive.read("SKILL.md").decode("utf-8")
        expected_meta = {
            "name": "chengzicv",
            "slug": "chengzicv-career-skills",
            "version": version,
            "displayName": "ChengziCV 全链路求职 Skills",
        }
        for key, expected in expected_meta.items():
            actual = frontmatter_value(root_text, key)
            if actual != expected:
                fail(f"SkillHub root {key} mismatch: {actual!r} != {expected!r}")
        if "../chengzicv-" in root_text:
            fail("SkillHub root still contains unpackaged sibling paths")
        if "[执行流程](WORKFLOW.md)" not in root_text:
            fail("SkillHub overview does not link to its execution workflow")
        if archive.read("WORKFLOW.md") != render_skillhub_workflow():
            fail("SkillHub workflow differs from the canonical routing instructions")
        if re.search(r"<(?:div|picture|img|source)\b|```mermaid", root_text):
            fail("SkillHub overview contains unsupported README markup")

        # Verify every runtime file, not just each child's entrypoint.
        # This catches missing onboarding/references and accidental content changes.
        for _, skill_name in PUBLIC_SKILLS:
            skill_dir = validate_skill(skill_name)
            for path in iter_runtime_files(skill_dir):
                relative = path.relative_to(skill_dir).as_posix()
                if skill_name == "chengzicv" and relative == "SKILL.md":
                    continue
                packaged = relative if skill_name == "chengzicv" else f"skills/{skill_name}/{relative}"
                if packaged not in names or archive.read(packaged) != public_runtime_bytes(path):
                    fail(f"SkillHub runtime file is missing or changed: {packaged}")

        actual_children = {
            parts[1]
            for name in names
            if len(parts := PurePosixPath(name).parts) >= 3 and parts[0] == "skills"
        }
        expected_children = {name for _, name in PUBLIC_SKILLS if name != "chengzicv"}
        if actual_children != expected_children:
            fail(
                f"SkillHub children differ: expected={sorted(expected_children)} "
                f"actual={sorted(actual_children)}"
            )
        verify_relative_markdown_links(archive)


def main() -> int:
    version = read_version()
    verify_github_bundle()
    verify_skillhub_bundle(version)
    print(f"Verified GitHub and SkillHub packages for v{version}")
    print(f"Public components: {len(PUBLIC_SKILLS)}; internal components included: 0")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
