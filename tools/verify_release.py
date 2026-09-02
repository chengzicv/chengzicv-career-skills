#!/usr/bin/env python3
"""Verify ChengziCV GitHub and SkillHub release archives."""

from __future__ import annotations

import io
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
    read_version,
)


FORBIDDEN_PARTS = {".DS_Store", "__pycache__", "candidate-data", "local-data", "outputs"}
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


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
        expected = {"README.md"}
        expected.update(f"{group}/{name}.zip" for group, name in PUBLIC_SKILLS)
        if set(names) != expected:
            fail(f"GitHub bundle entries differ: expected={sorted(expected)} actual={sorted(names)}")

        for group, skill_name in PUBLIC_SKILLS:
            member = f"{group}/{skill_name}.zip"
            with zipfile.ZipFile(io.BytesIO(outer.read(member))) as nested:
                nested_names = nested.namelist()
                validate_names(nested_names, member)
                if "SKILL.md" not in nested_names:
                    fail(f"{member} has no SKILL.md")
                if "agents/openai.yaml" not in nested_names:
                    fail(f"{member} has no agents/openai.yaml")
                skill_text = nested.read("SKILL.md").decode("utf-8")
                if frontmatter_value(skill_text, "name") != skill_name:
                    fail(f"{member} frontmatter name mismatch")


def verify_skillhub_bundle(version: str) -> None:
    asset = SKILLHUB_OUTPUT / f"chengzicv-career-skills-{version}.zip"
    if not asset.is_file():
        fail(f"missing SkillHub bundle: {asset}")
    with zipfile.ZipFile(asset) as archive:
        names = archive.namelist()
        validate_names(names, "SkillHub bundle")
        required = {"SKILL.md", "agents/openai.yaml", "LICENSE"}
        required.update(
            f"skills/{skill_name}/SKILL.md"
            for _, skill_name in PUBLIC_SKILLS
            if skill_name != "chengzicv"
        )
        missing = sorted(required - set(names))
        if missing:
            fail(f"SkillHub bundle is missing: {missing}")

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
