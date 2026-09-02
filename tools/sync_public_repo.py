#!/usr/bin/env python3
"""Export public ChengziCV files from the canonical local Skills repository."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from build_release import INTERNAL_SKILLS, PACKAGE_ROOT, PUBLIC_SKILLS, SKILLS_ROOT


PUBLIC_ROOT_FILES = (
    ".gitignore",
    "DEPENDENCIES.md",
    "LICENSE",
    "PACKAGING.md",
    "README.md",
    "VERSION",
)
PUBLIC_ROOT_DIRS = (".github", "assets", "evals", "tools")


def replace_copy(source: Path, target: Path) -> None:
    if target.exists():
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        else:
            target.unlink()
    if source.is_dir():
        shutil.copytree(
            source,
            target,
            ignore=shutil.ignore_patterns(".DS_Store", "__pycache__", "*.pyc", "dist"),
        )
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def validate_source() -> None:
    for _, skill_name in PUBLIC_SKILLS:
        if not (SKILLS_ROOT / skill_name / "SKILL.md").is_file():
            raise ValueError(f"missing source Skill: {skill_name}")
    for name in PUBLIC_ROOT_FILES:
        if not (PACKAGE_ROOT / name).is_file():
            raise ValueError(f"missing package file: {name}")


def sync(target: Path) -> None:
    target = target.expanduser().resolve()
    if target == PACKAGE_ROOT.resolve() or target == SKILLS_ROOT.resolve():
        raise ValueError("target must be a separate clean clone, not the source repository")
    if not (target / ".git").exists():
        raise ValueError(f"target is not a Git clone: {target}")

    validate_source()
    target.mkdir(parents=True, exist_ok=True)
    public_names = {name for _, name in PUBLIC_SKILLS}

    for existing in target.glob("chengzicv*"):
        if existing.is_dir() and existing.name not in public_names:
            shutil.rmtree(existing)

    for skill_name in sorted(public_names):
        replace_copy(SKILLS_ROOT / skill_name, target / skill_name)
    for name in PUBLIC_ROOT_FILES:
        replace_copy(PACKAGE_ROOT / name, target / name)
    for name in PUBLIC_ROOT_DIRS:
        source = PACKAGE_ROOT / name
        if source.exists():
            replace_copy(source, target / name)

    for internal in INTERNAL_SKILLS:
        if (target / internal).exists():
            raise ValueError(f"internal Skill leaked into public target: {internal}")
    print(f"Synced {len(public_names)} public ChengziCV components to {target}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="clean clone of chengzicv/chengzicv-career-skills")
    args = parser.parse_args()
    sync(Path(args.target))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
