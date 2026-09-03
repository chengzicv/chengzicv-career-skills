"""Regression coverage for the storefront/execution split, without installing Skills."""

from __future__ import annotations

import re
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import build_release as build
import verify_release as verify


class OverviewTests(unittest.TestCase):
    def test_overview_has_all_public_skills_and_compatible_versioned_logo(self):
        overview = build.render_skillhub_overview("1.2.2")
        names = re.findall(r"^\| `/([a-z0-9-]+)` \|", overview, re.MULTILINE)
        self.assertCountEqual(names, [name for _, name in build.PUBLIC_SKILLS])
        self.assertIn("/v1.2.2/assets/chengzicv-logo-skillhub.svg", overview)
        self.assertNotRegex(overview, r"<(?:div|picture|img|source)\b|```mermaid")
        self.assertNotIn("chengzicv-light-business-intake", overview)
        self.assertIn(build.SKILLHUB_URL, overview)
        self.assertIn("[执行流程](WORKFLOW.md)", overview)

    def test_overview_tracks_readme_instead_of_a_second_copy(self):
        readme = (build.PACKAGE_ROOT / "README.md").read_text(encoding="utf-8")
        changed = readme.replace("每个 Skill 都可以单独使用。", "这里是一条更新后的项目介绍。", 1)
        with patch.object(Path, "read_text", return_value=changed):
            self.assertIn("这里是一条更新后的项目介绍。", build.render_skillhub_overview("1.2.2"))

    def test_sized_logo_keeps_the_original_artwork(self):
        import base64
        import xml.etree.ElementTree as ET

        svg = ET.fromstring(build.render_skillhub_logo())
        self.assertEqual(svg.attrib["width"], "280")
        image = svg.find("{http://www.w3.org/2000/svg}image")
        encoded = image.attrib["href"].split(",", 1)[1]
        readme = (build.PACKAGE_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertEqual(base64.b64decode(encoded), (build.PACKAGE_ROOT / build.readme_logo_path(readme)).read_bytes())
        self.assertEqual((build.PACKAGE_ROOT / build.SKILLHUB_LOGO).read_text(encoding="utf-8"), build.render_skillhub_logo())

    def test_missing_readme_section_fails_instead_of_silently_omitting_content(self):
        readme = (build.PACKAGE_ROOT / "README.md").read_text(encoding="utf-8")
        changed = readme.replace("## 安装后怎么开始？", "## 已移动的章节")
        with patch.object(Path, "read_text", return_value=changed):
            with self.assertRaisesRegex(ValueError, "missing required section"):
                build.render_skillhub_overview("1.2.2")

    def test_missing_or_duplicate_public_entry_fails(self):
        readme = (build.PACKAGE_ROOT / "README.md").read_text(encoding="utf-8")
        changed = readme.replace("| `/chengzicv-update` |", "| `/chengzicv` |")
        with patch.object(Path, "read_text", return_value=changed):
            with self.assertRaisesRegex(ValueError, "public Skill list"):
                build.render_skillhub_overview("1.2.2")

    def test_logo_cannot_escape_repository_assets(self):
        readme = (build.PACKAGE_ROOT / "README.md").read_text(encoding="utf-8")
        for target in ("../private.png", "https://example.com/logo.png", "/private.png"):
            with self.subTest(target=target):
                changed = readme.replace('src="assets/chengzicv-logo-light.webp"', f'src="{target}"')
                with patch.object(Path, "read_text", return_value=changed):
                    with self.assertRaisesRegex(ValueError, "repository asset"):
                        build.render_skillhub_overview("1.2.2")

    def test_full_workflow_and_discovery_metadata_are_preserved(self):
        source = (build.SKILLS_ROOT / "chengzicv/SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n", source, re.DOTALL)
        expected = source[match.end():].replace("../chengzicv-", "skills/chengzicv-")
        self.assertEqual(build.render_skillhub_workflow().decode("utf-8"), expected)
        root = build.render_skillhub_root("1.2.2").decode("utf-8")
        for key in ("name", "description"):
            self.assertEqual(verify.frontmatter_value(root, key), verify.frontmatter_value(source, key))
        self.assertIn("onboarding/core-introduction.md", expected)
        self.assertNotIn("## 路由规则", root)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="chengzicv-overview-test-")
        self.addCleanup(self.temp.cleanup)
        output = Path(self.temp.name)
        for module in (build, verify):
            patcher = patch.multiple(module, GITHUB_OUTPUT=output, SKILLHUB_OUTPUT=output)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.version = build.read_version()
        self.github = build.build_github_bundle(self.version)
        self.hub = build.build_skillhub_bundle(self.version)

    def rewrite_hub(self, *, remove=None, replace=None):
        with zipfile.ZipFile(self.hub) as archive:
            contents = {name: archive.read(name) for name in archive.namelist()}
        if remove:
            contents.pop(remove)
        if replace:
            contents.update(replace)
        with zipfile.ZipFile(self.hub, "w") as archive:
            for name, content in contents.items():
                build.add_bytes(archive, name, content)

    def test_both_packages_and_all_relative_links_validate(self):
        verify.verify_github_bundle()
        verify.verify_skillhub_bundle(self.version)

    def test_packages_are_deterministic(self):
        first = self.hub.read_bytes()
        self.assertEqual(build.build_skillhub_bundle(self.version).read_bytes(), first)
        first = self.github.read_bytes()
        self.assertEqual(build.build_github_bundle(self.version).read_bytes(), first)

    def test_removing_or_rewriting_workflow_is_rejected(self):
        self.rewrite_hub(replace={"WORKFLOW.md": b"replacement"})
        with self.assertRaisesRegex(ValueError, "workflow differs"):
            verify.verify_skillhub_bundle(self.version)
        self.rewrite_hub(remove="WORKFLOW.md")
        with self.assertRaisesRegex(ValueError, "is missing"):
            verify.verify_skillhub_bundle(self.version)

    def test_missing_onboarding_is_rejected(self):
        self.rewrite_hub(remove="onboarding/core-introduction.md")
        with self.assertRaisesRegex(ValueError, "runtime file is missing"):
            verify.verify_skillhub_bundle(self.version)

    def test_rewriting_a_child_skill_is_rejected(self):
        self.rewrite_hub(replace={"skills/chengzicv-resume/SKILL.md": b"replacement"})
        with self.assertRaisesRegex(ValueError, "runtime file is missing or changed"):
            verify.verify_skillhub_bundle(self.version)

    def test_unlinked_workflow_is_rejected(self):
        with zipfile.ZipFile(self.hub) as archive:
            root = archive.read("SKILL.md").replace(b"(WORKFLOW.md)", b"(missing.md)")
        self.rewrite_hub(replace={"SKILL.md": root})
        with self.assertRaisesRegex(ValueError, "does not link"):
            verify.verify_skillhub_bundle(self.version)


if __name__ == "__main__":
    unittest.main()
