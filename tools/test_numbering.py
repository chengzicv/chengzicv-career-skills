"""回归门：README 的迭代编号与发行版号不混淆（规则见 PACKAGING.md「版本号与对用户的编号」）。

对用户只暴露「第 N 版」；`VERSION` 与 Git tag 的 `1.M.x` 只服务发版机制。
发布工作流从 README 第一条「第 N 版」解析 Release 标题，两处一旦漂移必须让构建失败。
"""

from __future__ import annotations

import re
import unittest

import build_release as build

ENTRY = re.compile(r"\*\*第 (\d+) 版\*\*")


class NumberingTests(unittest.TestCase):
    def setUp(self):
        self.readme = (build.PACKAGE_ROOT / "README.md").read_text(encoding="utf-8")

    def test_readme_has_iteration_entries_in_descending_order(self):
        numbers = [int(value) for value in ENTRY.findall(self.readme)]
        self.assertTrue(numbers, "README 更新日志缺少「第 N 版」条目")
        self.assertEqual(
            numbers,
            sorted(numbers, reverse=True),
            f"版本条目不是从新到旧排列：{numbers}",
        )

    def test_release_title_can_be_derived_from_readme(self):
        match = ENTRY.search(self.readme)
        self.assertIsNotNone(match, "发布工作流无法从 README 解析出编号")
        self.assertGreater(int(match.group(1)), 0)

    def test_no_semver_string_leaks_into_readme(self):
        leaked = re.findall(r"\bv\d+\.\d+\.\d+\b", self.readme)
        self.assertEqual(leaked, [], f"README 里不应出现 SemVer 串：{leaked}")


if __name__ == "__main__":
    unittest.main()
