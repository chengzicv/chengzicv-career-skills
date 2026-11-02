"""Regression checks for omitted resumes, review gates, and old manifests."""

from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("case_manifest.py")
EXAMPLES = SCRIPT.parent.parent / "references" / "examples"


class CaseManifestContractTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = self.root / "_内部" / "manifest.json"
        self.cli("init", self.manifest, "--batch-id", "test", "--expected-count", "2")
        self.cli("add", self.manifest, "--case-id", "CASE-001", "--industry", "生活用品", "--job-title", "供应链专员")

    def cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def read(self):
        return json.loads(self.manifest.read_text())

    def write(self, data):
        self.manifest.write_text(json.dumps(data, ensure_ascii=False))

    def prepare_article(self):
        role = self.root / "role"
        role.mkdir(exist_ok=True)
        shutil.copyfile(EXAMPLES / "supply-chain-specialist-job-guide.md", role / "03.md")
        data = self.read()
        case = data["cases"][0]
        case["sources"] = [{"category": "job", "title": "招聘测试样本", "url": "https://example.com/job", "accessed_at": "2026-08-31", "used_for": "验证来源结构"}]
        case["outputs"]["job_guide"] = "../role/03.md"
        self.write(data)
        self.cli("set-stage", self.manifest, "CASE-001", "research", "complete")
        self.cli("set-stage", self.manifest, "CASE-001", "job_guide", "complete")

    def prepare_resume(self):
        (self.root / "role" / "01.md").write_text(
            "# 小橙\n\n## 个人优势\n\n- **职业背景：** 测试用虚拟案例。\n\n## 教育背景\n\n测试用简历正文。\n",
            encoding="utf-8",
        )
        data = self.read()
        data["cases"][0]["additional_deliverables"]["virtual_resume"] = {"status": "complete", "path": "../role/01.md"}
        self.write(data)

    def test_default_includes_resume_and_user_review(self):
        data = self.read()
        self.assertEqual(set(data["required_deliverables"]), {"job_guide", "virtual_resume"})
        self.assertFalse(data["cases"][0]["user_review"]["approved"])
        self.prepare_article()
        before = self.manifest.read_bytes()
        error = self.cli("set-stage", self.manifest, "CASE-001", "audit", "complete", ok=False)
        self.assertIn("缺少已完成的虚拟简历", error)
        self.assertEqual(self.manifest.read_bytes(), before)

    def test_both_files_complete_does_not_approve_user_review(self):
        self.prepare_article()
        self.prepare_resume()
        self.cli("set-stage", self.manifest, "CASE-001", "audit", "complete")
        self.cli("validate", self.manifest, "--check-files")
        case = self.read()["cases"][0]
        self.assertEqual(case["status"], "complete")
        self.assertFalse(case["user_review"]["approved"])

    def test_resume_missing_empty_or_same_as_article_fails(self):
        self.prepare_article()
        self.prepare_resume()
        resume = self.root / "role" / "01.md"
        resume.unlink()
        self.assertIn("找不到独立正文文件", self.cli("validate", self.manifest, "--check-files", ok=False))
        resume.write_text("")
        self.assertIn("正文为空", self.cli("validate", self.manifest, "--check-files", ok=False))
        data = self.read()
        data["cases"][0]["additional_deliverables"]["virtual_resume"]["path"] = "../role/03.md"
        self.write(data)
        self.assertIn("重复 正文路径", self.cli("validate", self.manifest, "--check-files", ok=False))

    def test_next_role_waits_for_user_approval(self):
        self.prepare_article()
        self.prepare_resume()
        self.cli("set-stage", self.manifest, "CASE-001", "audit", "complete")
        self.cli("add", self.manifest, "--case-id", "CASE-002", "--industry", "制造业", "--job-title", "采购专员")
        before = self.manifest.read_bytes()
        error = self.cli("set-stage", self.manifest, "CASE-002", "research", "in_progress", ok=False)
        self.assertIn("尚未通过用户审核", error)
        self.assertEqual(self.manifest.read_bytes(), before)
        data = self.read()
        data["cases"][0]["user_review"] = {"status": "approved", "approved": True}
        self.write(data)
        self.cli("set-stage", self.manifest, "CASE-002", "research", "in_progress")

    def test_old_article_only_manifest_still_completes(self):
        data = self.read()
        data.pop("required_deliverables")
        data.pop("workflow")
        data["cases"][0].pop("additional_deliverables")
        data["cases"][0].pop("user_review")
        self.write(data)
        self.prepare_article()
        self.cli("set-stage", self.manifest, "CASE-001", "audit", "complete")
        self.cli("validate", self.manifest, "--check-files")

    def test_existing_user_requested_deliverables_are_checked(self):
        data = self.read()
        data["user_requested_deliverables"] = data.pop("required_deliverables")
        self.write(data)
        self.prepare_article()
        self.assertIn("虚拟简历", self.cli("set-stage", self.manifest, "CASE-001", "audit", "complete", ok=False))

    def test_explicit_article_only_and_legacy_modes(self):
        article = self.root / "article-only.json"
        self.cli("init", article, "--batch-id", "article", "--expected-count", "1", "--job-guide-only")
        self.assertEqual(json.loads(article.read_text())["required_deliverables"], ["job_guide"])
        legacy = self.root / "legacy.json"
        self.cli("init", legacy, "--batch-id", "legacy", "--expected-count", "1", "--delivery-mode", "legacy_deep")
        self.cli("add", legacy, "--case-id", "CASE-001", "--industry", "服务", "--job-title", "实施助理")
        old = json.loads(legacy.read_text())
        self.assertEqual(old["schema_version"], "1.1")
        self.assertNotIn("required_deliverables", old)
        self.assertIn("resume", old["cases"][0]["stages"])


if __name__ == "__main__":
    unittest.main()
