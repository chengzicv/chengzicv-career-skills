"""回归门：UPDATE.json 与 version.txt 必须和 VERSION 同步，否则构建失败。

这两个文件决定用户端的更新提醒：清单版本高了会提示升级，version.txt 是用户侧比对的本地版本。
任何一处漂移都会让提醒要么永远不出现，要么永远提示升级。
测试只校验纯函数，不写仓库里的真实文件。
"""

from __future__ import annotations

import json
import unittest

import build_release as build


class UpdateManifestTests(unittest.TestCase):
    def setUp(self):
        self.version = build.read_version()
        self.manifest = json.loads((build.PACKAGE_ROOT / "UPDATE.json").read_text(encoding="utf-8"))

    def check(self, **overrides):
        data = dict(self.manifest, **overrides)
        runtime = overrides.pop("runtime_version", self.version)
        build.validate_update_data(data, self.version, runtime)

    def test_current_manifest_is_valid(self):
        result = build.validate_update_manifest(self.version)
        self.assertEqual(result["version"], self.version)
        self.assertGreater(result["edition"], 0)

    def test_version_drift_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "does not match VERSION"):
            self.check(version="0.0.1")

    def test_overlong_notice_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "1-80"):
            self.check(notice="长" * 81)

    def test_notice_with_line_break_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "line breaks"):
            self.check(notice="第一行\n第二行")

    def test_bad_edition_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "positive integer"):
            self.check(edition=0)

    def test_non_https_details_url_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "https"):
            self.check(details_url="http://example.com")

    def test_runtime_version_drift_is_rejected(self):
        data = dict(self.manifest)
        with self.assertRaisesRegex(ValueError, "version.txt must match VERSION"):
            build.validate_update_data(data, self.version, "0.0.1")

    def test_missing_manifest_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "must be a JSON object"):
            build.validate_update_data([], self.version, self.version)


if __name__ == "__main__":
    unittest.main()
