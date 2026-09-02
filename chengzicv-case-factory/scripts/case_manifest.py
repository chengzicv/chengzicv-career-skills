#!/usr/bin/env python3
"""管理虚拟简历与岗位入门批次，兼容旧版单文章和深度案例批次。"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.1"
GUIDE_SCHEMA_VERSION = "1.2"
GUIDE_STAGES = ("selection", "research", "job_guide", "audit")
GUIDE_FORBIDDEN_TEXT = (
    "没有后台", "没有上线", "没有改口就不要编", "不虚构增长",
    "请替换数字", "不能直接投递", "不保证 offer", "不保证offer",
    "有实习更好", "Manifest", "CASE-ID", "质量门",
    "reference_only", "practice_ready", "resume_eligible",
)
INTERPRETATIONS = {"pairs", "cartesian", "custom"}
STAGES = (
    "selection",
    "research",
    "company_model",
    "resume",
    "portfolio",
    "interview_handbook",
    "student_practice",
    "audit",
)
STAGE_STATES = {"pending", "in_progress", "complete", "blocked", "skipped"}
CASE_STATES = {"planned", "in_progress", "complete", "blocked"}
REFERENCE_OUTPUT_KEYS = ("research_design", "resume", "portfolio", "interview_handbook")
PRACTICE_OUTPUT_KEYS = ("student_practice_pack", "evidence_template", "starter_data")
SOURCE_CATEGORIES = {"product", "constraint", "job"}
DISCLOSURE_MARKERS = ("教学示例", "教学案例", "教学材料", "非真实候选人", "虚拟案例")
PRACTICE_STATES = {
    "reference_only",
    "practice_ready",
    "executed_unverified",
    "evidence_verified",
    "real_experience_verified",
}
RESUME_ELIGIBLE_STATES = {"evidence_verified", "real_experience_verified"}
RESOURCE_DEPENDENCIES = {"unassessed", "low", "medium", "high"}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise ValueError(f"Manifest 不存在：{path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Manifest 不是有效 JSON：{exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Manifest 顶层必须是对象。")
    return data


def atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary_name, path)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)


def normalize_pair(industry: str, job_title: str) -> tuple[str, str]:
    return ("".join(industry.split()).casefold(), "".join(job_title.split()).casefold())


def get_case(data: dict[str, Any], case_id: str) -> dict[str, Any]:
    for case in data.get("cases", []):
        if case.get("case_id") == case_id:
            return case
    raise ValueError(f"找不到案例：{case_id}")


def derive_case_status(case: dict[str, Any]) -> str:
    stages = case.get("stages", {})
    values = [stages.get(stage, "pending") for stage in STAGES]
    if any(value == "blocked" for value in values):
        return "blocked"
    if all(value in {"complete", "skipped"} for value in values):
        return "complete"
    if any(value in {"in_progress", "complete", "skipped"} for value in values):
        return "in_progress"
    return "planned"


def command_init(args: argparse.Namespace) -> int:
    if getattr(args, "job_guide_only", False) and args.delivery_mode != "job_guide":
        raise ValueError("--job-guide-only 仅用于 job_guide 模式")
    if args.delivery_mode == "job_guide":
        return command_guide_init(args)
    path = Path(args.manifest).expanduser().resolve()
    if path.exists():
        print(f"拒绝覆盖已有 Manifest：{path}", file=sys.stderr)
        return 2
    timestamp = now_iso()
    data = {
        "schema_version": SCHEMA_VERSION,
        "batch_id": args.batch_id,
        "interpretation": args.interpretation,
        "expected_case_count": args.expected_count,
        "default_candidate_name": args.candidate_name,
        "created_at": timestamp,
        "updated_at": timestamp,
        "cases": [],
    }
    atomic_write(path, data)
    print(f"已创建：{path}")
    return 0


def command_add(args: argparse.Namespace) -> int:
    path = Path(args.manifest).expanduser().resolve()
    data = load_manifest(path)
    if is_job_guide(data):
        return command_guide_add(args, path, data)
    cases = data.setdefault("cases", [])
    if any(case.get("case_id") == args.case_id for case in cases):
        print(f"案例 ID 已存在：{args.case_id}", file=sys.stderr)
        return 2
    pair = normalize_pair(args.industry, args.job_title)
    if any(
        normalize_pair(str(case.get("industry", "")), str(case.get("job_title", "")))
        == pair
        for case in cases
    ):
        print(f"行业岗位组合已存在：{args.industry} × {args.job_title}", file=sys.stderr)
        return 2
    candidate_name = args.candidate_name or data.get("default_candidate_name") or "小橙"
    case = {
        "case_id": args.case_id,
        "industry": args.industry,
        "job_title": args.job_title,
        "candidate_name": candidate_name,
        "level": args.level,
        "city": args.city,
        "company_model": args.company_model,
        "status": "in_progress",
        "stages": {
            stage: ("complete" if stage == "selection" else "pending")
            for stage in STAGES
        },
        "uniqueness": {
            "business_trigger": "",
            "primary_constraint": "",
            "failure_type": "",
            "stop_decision": "",
            "evidence_form": "",
        },
        "adaptation": {
            "reference_status": "reference_only",
            "evidence_state": "reference_only",
            "resume_eligible": False,
            "resource_dependency": "unassessed",
            "non_substitutable_gap": "",
            "evidence_basis": [],
            "reference_only_entities": [],
        },
        "sources": [],
        "outputs": {},
        "blocked_reason": "",
        "notes": [],
    }
    cases.append(case)
    data["updated_at"] = now_iso()
    atomic_write(path, data)
    print(f"已添加：{args.case_id}｜{args.industry} × {args.job_title}｜{candidate_name}")
    return 0


def command_set_stage(args: argparse.Namespace) -> int:
    path = Path(args.manifest).expanduser().resolve()
    data = load_manifest(path)
    if is_job_guide(data):
        return command_guide_set_stage(args, path, data)
    if args.stage not in STAGES:
        raise ValueError("旧版批次不支持该阶段")
    case = get_case(data, args.case_id)
    stages = case.setdefault("stages", {})
    stages[args.stage] = args.state
    if args.note:
        case.setdefault("notes", []).append(args.note)
    if args.state == "blocked" and args.note:
        case["blocked_reason"] = args.note
    elif args.state != "blocked" and case.get("blocked_reason"):
        case["blocked_reason"] = ""
    case["status"] = derive_case_status(case)
    data["updated_at"] = now_iso()
    atomic_write(path, data)
    print(f"已更新：{args.case_id}｜{args.stage}={args.state}｜status={case['status']}")
    return 0


def command_set_evidence(args: argparse.Namespace) -> int:
    path = Path(args.manifest).expanduser().resolve()
    data = load_manifest(path)
    if is_job_guide(data):
        raise ValueError("岗位普及文章不进入个人实践证据流程；真实简历由 resume Skill 处理")
    case = get_case(data, args.case_id)
    adaptation = case.setdefault("adaptation", {})
    evidence_basis = adaptation.get("evidence_basis", [])
    if not isinstance(evidence_basis, list):
        raise ValueError(f"{args.case_id}.adaptation.evidence_basis 不是数组")
    for item in args.evidence:
        normalized = item.strip()
        if normalized and normalized not in evidence_basis:
            evidence_basis.append(normalized)

    resource_dependency = (
        args.resource_dependency
        or adaptation.get("resource_dependency")
        or "unassessed"
    )
    gap = (
        args.non_substitutable_gap
        if args.non_substitutable_gap is not None
        else str(adaptation.get("non_substitutable_gap", ""))
    )
    if args.state != "reference_only" and resource_dependency == "unassessed":
        raise ValueError("进入学生实践前必须设置 --resource-dependency low/medium/high")
    if args.state in {
        "executed_unverified",
        "evidence_verified",
        "real_experience_verified",
    } and not any(str(item).strip() for item in evidence_basis):
        raise ValueError("进入已执行或已验证状态前，至少提供一个 --evidence 证据路径")
    if (
        resource_dependency == "high"
        and args.state != "reference_only"
        and not gap.strip()
    ):
        raise ValueError("高资源实践必须提供 --non-substitutable-gap")

    adaptation.update(
        {
            "reference_status": "reference_only",
            "evidence_state": args.state,
            "resume_eligible": args.state in RESUME_ELIGIBLE_STATES,
            "resource_dependency": resource_dependency,
            "non_substitutable_gap": gap,
            "evidence_basis": evidence_basis,
        }
    )
    if args.note:
        case.setdefault("notes", []).append(args.note)
    data["updated_at"] = now_iso()
    atomic_write(path, data)
    print(
        f"已更新：{args.case_id}｜evidence_state={args.state}｜"
        f"resume_eligible={str(adaptation['resume_eligible']).lower()}｜"
        f"evidence={len(evidence_basis)}"
    )
    return 0


def validate_manifest(
    data: dict[str, Any], path: Path, check_files: bool
) -> tuple[list[str], list[str]]:
    if is_job_guide(data):
        return validate_job_guide_manifest(data, path, check_files)
    if data.get("delivery_mode") not in (None, "legacy_deep"):
        return ["delivery_mode 非法"], []
    errors: list[str] = []
    warnings: list[str] = []

    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version 应为 {SCHEMA_VERSION}")
    if not str(data.get("batch_id", "")).strip():
        errors.append("缺少 batch_id")
    if data.get("interpretation") not in INTERPRETATIONS:
        errors.append("interpretation 必须是 pairs、cartesian 或 custom")
    expected = data.get("expected_case_count")
    if not isinstance(expected, int) or expected <= 0:
        errors.append("expected_case_count 必须是正整数")
    if not str(data.get("default_candidate_name", "")).strip():
        errors.append("default_candidate_name 不能为空")

    cases = data.get("cases")
    if not isinstance(cases, list):
        errors.append("cases 必须是数组")
        return errors, warnings
    if isinstance(expected, int) and expected != len(cases):
        warnings.append(f"目标 {expected} 套，当前清单 {len(cases)} 套")

    ids: list[str] = []
    pairs: list[tuple[str, str]] = []
    for index, case in enumerate(cases, start=1):
        prefix = f"cases[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{prefix} 必须是对象")
            continue
        case_id = str(case.get("case_id", "")).strip()
        industry = str(case.get("industry", "")).strip()
        job_title = str(case.get("job_title", "")).strip()
        if not case_id:
            errors.append(f"{prefix} 缺少 case_id")
        else:
            ids.append(case_id)
        if not industry:
            errors.append(f"{prefix} 缺少 industry")
        if not job_title:
            errors.append(f"{prefix} 缺少 job_title")
        if industry and job_title:
            pairs.append(normalize_pair(industry, job_title))
        if not str(case.get("candidate_name", "")).strip():
            errors.append(f"{prefix} 缺少 candidate_name")
        if case.get("status") not in CASE_STATES:
            errors.append(f"{prefix}.status 非法")

        stages = case.get("stages")
        if not isinstance(stages, dict):
            errors.append(f"{prefix}.stages 必须是对象")
            stages = {}
        for stage in STAGES:
            if stages.get(stage) not in STAGE_STATES:
                errors.append(f"{prefix}.stages.{stage} 非法或缺失")
        derived = derive_case_status(case)
        if case.get("status") != derived:
            warnings.append(
                f"{case_id or prefix} status={case.get('status')}，按阶段应为 {derived}"
            )

        sources = case.get("sources", [])
        if not isinstance(sources, list):
            errors.append(f"{prefix}.sources 必须是数组")
            sources = []
        if stages.get("research") == "complete":
            categories = {
                source.get("category")
                for source in sources
                if isinstance(source, dict)
            }
            missing = sorted(SOURCE_CATEGORIES - categories)
            if missing:
                errors.append(
                    f"{case_id or prefix} research 已完成但缺来源类别：{', '.join(missing)}"
                )
            for source_index, source in enumerate(sources, start=1):
                if not isinstance(source, dict):
                    errors.append(
                        f"{case_id or prefix}.sources[{source_index}] 必须是对象"
                    )
                    continue
                for key in ("category", "title", "url", "accessed_at", "used_for"):
                    if not str(source.get(key, "")).strip():
                        errors.append(
                            f"{case_id or prefix}.sources[{source_index}] 缺少 {key}"
                        )

        outputs = case.get("outputs", {})
        if not isinstance(outputs, dict):
            errors.append(f"{prefix}.outputs 必须是对象")
            outputs = {}

        adaptation = case.get("adaptation")
        if not isinstance(adaptation, dict):
            errors.append(f"{prefix}.adaptation 必须是对象")
            adaptation = {}
        reference_status = adaptation.get("reference_status")
        evidence_state = adaptation.get("evidence_state")
        resume_eligible = adaptation.get("resume_eligible")
        resource_dependency = adaptation.get("resource_dependency")
        evidence_basis = adaptation.get("evidence_basis")
        reference_only_entities = adaptation.get("reference_only_entities")
        if reference_status != "reference_only":
            errors.append(f"{case_id or prefix}.adaptation.reference_status 必须为 reference_only")
        if evidence_state not in PRACTICE_STATES:
            errors.append(f"{case_id or prefix}.adaptation.evidence_state 非法或缺失")
        if not isinstance(resume_eligible, bool):
            errors.append(f"{case_id or prefix}.adaptation.resume_eligible 必须是布尔值")
        elif evidence_state in PRACTICE_STATES:
            expected_eligibility = evidence_state in RESUME_ELIGIBLE_STATES
            if resume_eligible != expected_eligibility:
                errors.append(
                    f"{case_id or prefix} 的 resume_eligible 与 evidence_state={evidence_state} 不一致"
                )
        if resource_dependency not in RESOURCE_DEPENDENCIES:
            errors.append(f"{case_id or prefix}.adaptation.resource_dependency 非法或缺失")
        elif evidence_state != "reference_only" and resource_dependency == "unassessed":
            errors.append(f"{case_id or prefix} 已进入学生实践但资源依赖仍为 unassessed")
        if not isinstance(evidence_basis, list):
            errors.append(f"{case_id or prefix}.adaptation.evidence_basis 必须是数组")
            evidence_basis = []
        if not isinstance(reference_only_entities, list):
            errors.append(
                f"{case_id or prefix}.adaptation.reference_only_entities 必须是数组"
            )
            reference_only_entities = []
        if evidence_state in {
            "executed_unverified",
            "evidence_verified",
            "real_experience_verified",
        } and not any(str(item).strip() for item in evidence_basis):
            errors.append(f"{case_id or prefix} 已执行或验证但缺少 evidence_basis")
        if (
            resource_dependency == "high"
            and evidence_state != "reference_only"
            and not str(adaptation.get("non_substitutable_gap", "")).strip()
        ):
            errors.append(f"{case_id or prefix} 是高资源实践但缺少 non_substitutable_gap")

        def check_output(
            key: str,
            *,
            required_reason: str,
            disclosure_markers: tuple[str, ...] = (),
            required_markers: tuple[str, ...] = (),
        ) -> None:
            value = str(outputs.get(key, "")).strip()
            if not value:
                errors.append(f"{case_id or prefix} {required_reason}但缺少 outputs.{key}")
                return
            output_name = Path(value).name
            if case_id and case_id not in output_name:
                errors.append(f"{case_id or prefix} 的 {key} 文件名缺少案例 ID")
            if "案例" not in output_name and "示例" not in output_name:
                errors.append(f"{case_id or prefix} 的 {key} 文件名未标明案例/示例属性")
            output_path = path.parent / value
            if check_files and not output_path.exists():
                errors.append(f"{case_id or prefix} 找不到产物：{value}")
                return
            if not check_files or not disclosure_markers:
                return
            try:
                leading_text = output_path.read_text(encoding="utf-8")[:4000]
            except (OSError, UnicodeError) as exc:
                errors.append(f"{case_id or prefix} 无法读取产物 {value}：{exc}")
                return
            if not any(marker in leading_text for marker in disclosure_markers):
                errors.append(f"{case_id or prefix} 的 {key} 缺少材料属性披露")
            for marker in required_markers:
                if marker not in leading_text:
                    errors.append(f"{case_id or prefix} 的 {key} 缺少必需标记：{marker}")

        if stages.get("audit") == "complete":
            for key in REFERENCE_OUTPUT_KEYS:
                check_output(
                    key,
                    required_reason="audit 已完成",
                    disclosure_markers=DISCLOSURE_MARKERS,
                )

        if stages.get("student_practice") == "complete":
            if evidence_state == "reference_only":
                errors.append(
                    f"{case_id or prefix} student_practice 已完成但 evidence_state 仍为 reference_only"
                )
            check_output(
                "student_practice_pack",
                required_reason="student_practice 已完成",
                disclosure_markers=("学生实践任务",),
                required_markers=(
                    "practice_ready",
                    "resume_eligible=false",
                    "没有预设",
                    "真实偏差",
                    "不可替代缺口",
                    "绝对不能写",
                ),
            )
            check_output(
                "evidence_template",
                required_reason="student_practice 已完成",
                disclosure_markers=("实践记录", "证据模板"),
                required_markers=(
                    "practice_ready",
                    "resume_eligible=false",
                    "原始输入台账",
                    "执行日志",
                    "真实偏差",
                    "局限",
                    "面试诚实回答",
                ),
            )
            check_output("starter_data", required_reason="student_practice 已完成")
            if not reference_only_entities:
                errors.append(
                    f"{case_id or prefix} student_practice 已完成但未登记 reference_only_entities"
                )
            if check_files:
                for key in PRACTICE_OUTPUT_KEYS:
                    value = str(outputs.get(key, "")).strip()
                    output_path = path.parent / value
                    if not value or not output_path.exists():
                        continue
                    try:
                        practice_text = output_path.read_text(encoding="utf-8-sig")
                    except (OSError, UnicodeError):
                        continue
                    leaked = [
                        str(entity)
                        for entity in reference_only_entities
                        if str(entity).strip() and str(entity) in practice_text
                    ]
                    if leaked:
                        errors.append(
                            f"{case_id or prefix} 的 {key} 泄漏参考案例实体：{', '.join(leaked)}"
                        )
                task_value = str(outputs.get("student_practice_pack", "")).strip()
                task_path = path.parent / task_value
                gap = str(adaptation.get("non_substitutable_gap", "")).strip()
                if gap and task_value and task_path.exists():
                    try:
                        task_text = task_path.read_text(encoding="utf-8")
                    except (OSError, UnicodeError):
                        pass
                    else:
                        if gap not in task_text:
                            errors.append(
                                f"{case_id or prefix} 的学生实践任务包未原样披露 non_substitutable_gap"
                            )

    duplicate_ids = [value for value, count in Counter(ids).items() if count > 1]
    if duplicate_ids:
        errors.append(f"重复 case_id：{', '.join(sorted(duplicate_ids))}")
    duplicate_pairs = [pair for pair, count in Counter(pairs).items() if count > 1]
    if duplicate_pairs:
        readable = [f"{industry}×{job}" for industry, job in duplicate_pairs]
        errors.append(f"重复行业岗位组合：{', '.join(readable)}")

    return errors, warnings


def command_validate(args: argparse.Namespace) -> int:
    path = Path(args.manifest).expanduser().resolve()
    data = load_manifest(path)
    errors, warnings = validate_manifest(data, path, args.check_files)
    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(
            f"校验失败：{len(errors)} 个错误，{len(warnings)} 个警告",
            file=sys.stderr,
        )
        return 1
    print(f"校验通过：{len(data.get('cases', []))} 个案例，{len(warnings)} 个警告")
    return 0


def command_summary(args: argparse.Namespace) -> int:
    path = Path(args.manifest).expanduser().resolve()
    data = load_manifest(path)
    if is_job_guide(data):
        return command_guide_summary(data)
    cases = data.get("cases", [])
    status_counts = Counter(
        case.get("status", "unknown") for case in cases if isinstance(case, dict)
    )
    print(f"批次：{data.get('batch_id', '')}")
    print(
        f"范围：{data.get('interpretation', '')}｜目标 {data.get('expected_case_count', '')}｜当前 {len(cases)}"
    )
    print(f"默认候选人：{data.get('default_candidate_name', '')}")
    print(
        "案例状态："
        + "，".join(
            f"{key}={status_counts.get(key, 0)}"
            for key in ("planned", "in_progress", "complete", "blocked")
        )
    )
    evidence_counts = Counter(
        case.get("adaptation", {}).get("evidence_state", "missing")
        for case in cases
        if isinstance(case, dict)
    )
    eligible_count = sum(
        case.get("adaptation", {}).get("resume_eligible") is True
        for case in cases
        if isinstance(case, dict)
    )
    print(
        "实践状态："
        + "，".join(
            f"{state}={evidence_counts.get(state, 0)}"
            for state in (
                "reference_only",
                "practice_ready",
                "executed_unverified",
                "evidence_verified",
                "real_experience_verified",
            )
        )
    )
    print(f"简历准入：resume_eligible=true {eligible_count}｜false {len(cases) - eligible_count}")
    for stage in STAGES:
        counts = Counter(
            case.get("stages", {}).get(stage, "missing")
            for case in cases
            if isinstance(case, dict)
        )
        print(
            f"{stage}: "
            + "，".join(
                f"{state}={counts.get(state, 0)}"
                for state in (
                    "pending",
                    "in_progress",
                    "complete",
                    "blocked",
                    "skipped",
                )
            )
        )
    return 0


def is_job_guide(data: dict[str, Any]) -> bool:
    return (
        data.get("delivery_mode") == "job_guide"
        or data.get("schema_version") == GUIDE_SCHEMA_VERSION
    )


def guide_deliverables(data: dict[str, Any]) -> list[str]:
    # Absent declarations retain the old article-only contract.
    required = data.get("required_deliverables", data.get("user_requested_deliverables", ["job_guide"]))
    if (
        not isinstance(required, list)
        or not all(isinstance(item, str) for item in required)
        or "job_guide" not in required
        or set(required) - {"job_guide", "virtual_resume"}
        or len(required) != len(set(required))
    ):
        raise ValueError("required_deliverables 须包含 job_guide，可另含 virtual_resume，不可重复")
    return required


def validate_case_markdown(output: Path, label: str, disclosure_location: str | None) -> list[str]:
    errors: list[str] = []
    if output.suffix.lower() != ".md":
        errors.append(f"{label} 须为 Markdown 文件")
    if not output.is_file() or output.is_symlink():
        return errors + [f"{label} 找不到独立正文文件：{output}"]
    try:
        text = output.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        return errors + [f"{label} 读取正文失败：{exc}"]
    if not text.strip():
        errors.append(f"{label} 正文为空")
    if text.lstrip().startswith(("---\n", "---\r\n")):
        errors.append(f"{label} 正文不应包含 frontmatter")
    if len(re.findall(r"^# [^\n]+", text, re.MULTILINE)) != 1:
        errors.append(f"{label} 正文须有一个主标题")
    if len(re.findall(r"^## [^\n]+", text, re.MULTILINE)) < 2:
        errors.append(f"{label} 正文需有便于浏览的小标题")
    forbidden = [word for word in GUIDE_FORBIDDEN_TEXT if word in text]
    if forbidden:
        errors.append(f"{label} 正文包含制作旁白或内部标记：{', '.join(forbidden)}")
    if disclosure_location == "document" and not any(marker in text[:800] for marker in DISCLOSURE_MARKERS):
        errors.append(f"{label} 独立外发模式缺少一次案例说明")
    return errors


def guide_status(case: dict[str, Any]) -> str:
    stages = case.get("stages", {})
    if not isinstance(stages, dict):
        return "planned"
    values = [stages.get(stage, "pending") for stage in GUIDE_STAGES]
    if "blocked" in values:
        return "blocked"
    if all(value == "complete" for value in values):
        return "complete"
    if any(value != "pending" for value in values):
        return "in_progress"
    return "planned"


def command_guide_init(args: argparse.Namespace) -> int:
    path = Path(args.manifest).expanduser().resolve()
    if path.exists():
        raise ValueError(f"拒绝覆盖已有 Manifest：{path}")
    if args.expected_count <= 0 or not args.candidate_name.strip():
        raise ValueError("目标数量须为正整数，默认姓名不能为空")
    timestamp = now_iso()
    data = {
        "schema_version": GUIDE_SCHEMA_VERSION,
        "delivery_mode": "job_guide",
        "batch_id": args.batch_id,
        "interpretation": args.interpretation,
        "expected_case_count": args.expected_count,
        "default_candidate_name": args.candidate_name,
        "presentation": {"disclosure_location": "platform"},
        "required_deliverables": ["job_guide"] if args.job_guide_only else ["job_guide", "virtual_resume"],
        "workflow": {"mode": "sequential_user_review", "require_explicit_user_approval_before_next": True},
        "created_at": timestamp,
        "updated_at": timestamp,
        "cases": [],
    }
    atomic_write(path, data)
    print(f"已创建批次：{path}｜交付：{', '.join(data['required_deliverables'])}")
    return 0


def command_guide_add(args: argparse.Namespace, path: Path, data: dict[str, Any]) -> int:
    cases = data.setdefault("cases", [])
    if not all(value.strip() for value in (args.case_id, args.industry, args.job_title)):
        raise ValueError("案例 ID、行业和岗位不能为空")
    for case in cases:
        if case.get("case_id") == args.case_id:
            raise ValueError(f"案例 ID 已存在：{args.case_id}")
        if normalize_pair(str(case.get("industry", "")), str(case.get("job_title", ""))) == normalize_pair(args.industry, args.job_title):
            raise ValueError("行业岗位组合已存在")
    name = args.candidate_name or data.get("default_candidate_name") or "小橙"
    case = {
        "case_id": args.case_id,
        "industry": args.industry,
        "job_title": args.job_title,
        "candidate_name": name,
        "level": args.level,
        "city": args.city,
        "company_model": args.company_model,
        "stages": {stage: "complete" if stage == "selection" else "pending" for stage in GUIDE_STAGES},
        "adaptation": {"reference_status": "reference_only", "resume_eligible": False},
        "sources": [],
        "outputs": {},
        "user_review": {"status": "pending", "approved": False},
        "blocked_reason": "",
        "notes": [],
    }
    if "virtual_resume" in guide_deliverables(data):
        case["additional_deliverables"] = {"virtual_resume": {"status": "pending", "path": ""}}
    case["status"] = guide_status(case)
    cases.append(case)
    data["updated_at"] = now_iso()
    atomic_write(path, data)
    print(f"已添加：{args.case_id}｜{args.job_title}｜{name}｜交付：{', '.join(guide_deliverables(data))}")
    return 0


def command_guide_set_stage(args: argparse.Namespace, path: Path, data: dict[str, Any]) -> int:
    if args.stage not in GUIDE_STAGES or args.state == "skipped":
        raise ValueError("岗位入门只使用 selection、research、job_guide、audit，必需阶段不能跳过")
    case = get_case(data, args.case_id)
    case.setdefault("stages", {})[args.stage] = args.state
    if args.note:
        case.setdefault("notes", []).append(args.note)
    case["blocked_reason"] = args.note if args.state == "blocked" else ""
    case["status"] = guide_status(case)
    errors, _ = validate_job_guide_manifest(data, path, check_files=True)
    if errors:
        raise ValueError("；".join(errors))
    data["updated_at"] = now_iso()
    atomic_write(path, data)
    print(f"已更新：{args.case_id}｜{args.stage}={args.state}｜status={case['status']}")
    return 0


def validate_job_guide_manifest(
    data: dict[str, Any], path: Path, check_files: bool
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if data.get("schema_version") != GUIDE_SCHEMA_VERSION or data.get("delivery_mode") != "job_guide":
        errors.append("岗位入门批次须使用 schema_version=1.2、delivery_mode=job_guide")
    for key in ("batch_id", "default_candidate_name"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            errors.append(f"缺少 {key}")
    if data.get("interpretation") not in INTERPRETATIONS:
        errors.append("interpretation 必须是 pairs、cartesian 或 custom")
    expected = data.get("expected_case_count")
    if type(expected) is not int or expected <= 0:
        errors.append("expected_case_count 必须是正整数")
    presentation = data.get("presentation", {})
    location = presentation.get("disclosure_location") if isinstance(presentation, dict) else None
    if location not in ("platform", "document"):
        errors.append("presentation.disclosure_location 须为 platform 或 document")
    try:
        required_deliverables = guide_deliverables(data)
    except ValueError as exc:
        errors.append(str(exc))
        required_deliverables = ["job_guide"]
    workflow = data.get("workflow", {})
    sequential_review = isinstance(workflow, dict) and workflow.get("mode") == "sequential_user_review"
    cases = data.get("cases")
    if not isinstance(cases, list):
        return errors + ["cases 必须是数组"], warnings
    if type(expected) is int and expected != len(cases):
        warnings.append(f"目标 {expected} 篇，当前清单 {len(cases)} 篇")
    ids: list[str] = []
    pairs: list[tuple[str, str]] = []
    output_paths: list[str] = []
    for index, case in enumerate(cases, start=1):
        label = f"cases[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{label} 必须是对象")
            continue
        for key in ("case_id", "industry", "job_title", "candidate_name"):
            if not isinstance(case.get(key), str) or not case[key].strip():
                errors.append(f"{label} 缺少 {key}")
        ids.append(str(case.get("case_id", "")))
        pairs.append(normalize_pair(str(case.get("industry", "")), str(case.get("job_title", ""))))
        stages = case.get("stages")
        if not isinstance(stages, dict):
            errors.append(f"{label}.stages 必须是对象")
            stages = {}
        if set(stages) != set(GUIDE_STAGES):
            errors.append(f"{label} 阶段须为 selection、research、job_guide、audit")
        for stage_index, stage in enumerate(GUIDE_STAGES):
            state = stages.get(stage)
            if state not in STAGE_STATES - {"skipped"}:
                errors.append(f"{label}.{stage} 状态非法或跳过必需阶段")
            if state == "complete" and any(stages.get(previous) != "complete" for previous in GUIDE_STAGES[:stage_index]):
                errors.append(f"{label}.{stage} 完成前需先完成前序阶段")
        if case.get("status") != guide_status(case):
            errors.append(f"{label}.status 与阶段不一致")
        review = case.get("user_review", {})
        if not isinstance(review, dict):
            errors.append(f"{label}.user_review 必须是对象")
            review = {}
        if "approved" in review and type(review["approved"]) is not bool:
            errors.append(f"{label}.user_review.approved 必须为布尔值")
        if review.get("approved") is True and stages.get("audit") != "complete":
            errors.append(f"{label} 用户审核通过前需交齐材料并完成自查")
        if sequential_review and any(stages.get(stage) in {"in_progress", "complete"} for stage in GUIDE_STAGES[1:]):
            previous_reviews = [previous.get("user_review", {}) if isinstance(previous, dict) else {} for previous in cases[:index - 1]]
            if any(not isinstance(previous, dict) or previous.get("approved") is not True for previous in previous_reviews):
                errors.append(f"{label} 前序岗位尚未通过用户审核，不得开始本岗研究或写作")
        adaptation = case.get("adaptation", {})
        if (
            not isinstance(adaptation, dict)
            or adaptation.get("reference_status") != "reference_only"
            or adaptation.get("resume_eligible") is not False
        ):
            errors.append(f"{label} 岗位文章须保持 reference_only、resume_eligible=false")
        sources = case.get("sources", [])
        if not isinstance(sources, list):
            errors.append(f"{label}.sources 必须是数组")
            sources = []
        if stages.get("research") == "complete":
            if not any(isinstance(source, dict) and source.get("category") == "job" for source in sources):
                errors.append(f"{label} 缺少公开 JD 来源")
            for source in sources:
                if not isinstance(source, dict):
                    errors.append(f"{label} 来源须为对象")
                    continue
                for key in ("category", "title", "url", "accessed_at", "used_for"):
                    if not isinstance(source.get(key), str) or not source[key].strip():
                        errors.append(f"{label} 来源缺少 {key}")
                if not re.match(r"^https?://[^/\s]+", str(source.get("url", ""))):
                    errors.append(f"{label} 来源 URL 须为公开网页链接")
        extras = case.get("additional_deliverables", {})
        if not isinstance(extras, dict):
            errors.append(f"{label}.additional_deliverables 必须是对象")
            extras = {}
        resume = extras.get("virtual_resume", {})
        if not isinstance(resume, dict):
            errors.append(f"{label}.virtual_resume 必须是对象")
            resume = {}
        if "virtual_resume" in required_deliverables and stages.get("audit") == "complete" and resume.get("status") != "complete":
            errors.append(f"{label} 缺少已完成的虚拟简历，不能完成自查")
        resume_path = resume.get("path", "")
        if not isinstance(resume_path, str) or (resume.get("status") == "complete" and not resume_path.strip()):
            errors.append(f"{label} 缺少有效虚拟简历路径")
        elif resume_path:
            resume_output = path.parent / resume_path
            output_paths.append(str(resume_output.resolve()))
            if resume_output.suffix.lower() != ".md":
                errors.append(f"{label} 虚拟简历须为 Markdown 文件")
            if check_files:
                errors.extend(validate_case_markdown(resume_output, f"{label} 虚拟简历", location))
        outputs = case.get("outputs", {})
        if not isinstance(outputs, dict):
            errors.append(f"{label}.outputs 必须是对象")
            outputs = {}
        if set(outputs) - {"job_guide"}:
            errors.append(f"{label} outputs 只记录 job_guide；虚拟简历登记在 additional_deliverables.virtual_resume")
        value = outputs.get("job_guide", "")
        required = stages.get("job_guide") == "complete" or stages.get("audit") == "complete"
        if not isinstance(value, str) or (required and not value.strip()):
            errors.append(f"{label} 缺少有效 outputs.job_guide")
            continue
        if not value:
            continue
        output = path.parent / value
        if output.suffix.lower() != ".md":
            errors.append(f"{label} 岗位入门须为 Markdown 文件")
        output_paths.append(str(output.resolve()))
        if not check_files:
            continue
        errors.extend(validate_case_markdown(output, f"{label} 岗位入门", location))
    for values, name in ((ids, "case_id"), (pairs, "行业岗位组合"), (output_paths, "正文路径")):
        duplicates = [str(value) for value, count in Counter(values).items() if count > 1]
        if duplicates:
            errors.append(f"重复 {name}：{', '.join(duplicates)}")
    return errors, warnings


def command_guide_summary(data: dict[str, Any]) -> int:
    cases = data.get("cases", [])
    counts = Counter(case.get("status", "unknown") for case in cases if isinstance(case, dict))
    print(f"批次：{data.get('batch_id', '')}｜岗位入门｜目标 {data.get('expected_case_count', '')} 篇")
    print(f"默认人物：{data.get('default_candidate_name', '')}")
    print(f"必交文件：{', '.join(guide_deliverables(data))}")
    approved = sum(isinstance(case.get("user_review"), dict) and case["user_review"].get("approved") is True for case in cases if isinstance(case, dict))
    print(f"用户审核通过：{approved}/{len(cases)}；制作完成不等于用户认可")
    print("文章状态：" + "，".join(f"{key}={counts.get(key, 0)}" for key in ("planned", "in_progress", "complete", "blocked")))
    for case in cases:
        if isinstance(case, dict):
            print(f"{case.get('case_id', '')}｜{case.get('job_title', '')}｜{case.get('status', '')}｜{case.get('outputs', {}).get('job_guide', '')}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="创建空批次 Manifest")
    init_parser.add_argument("manifest")
    init_parser.add_argument("--batch-id", required=True)
    init_parser.add_argument("--expected-count", required=True, type=int)
    init_parser.add_argument(
        "--interpretation", choices=sorted(INTERPRETATIONS), default="pairs"
    )
    init_parser.add_argument("--candidate-name", default="小橙")
    init_parser.add_argument(
        "--delivery-mode", choices=("job_guide", "legacy_deep"), default="job_guide",
        help="默认虚拟简历＋岗位入门；legacy_deep 仅用于明确要求的旧版深度批次",
    )
    init_parser.add_argument("--job-guide-only", action="store_true", help="用户明确只要文章时使用，不要求虚拟简历")
    init_parser.set_defaults(func=command_init)

    add_parser = subparsers.add_parser("add", help="添加一个行业岗位案例")
    add_parser.add_argument("manifest")
    add_parser.add_argument("--case-id", required=True)
    add_parser.add_argument("--industry", required=True)
    add_parser.add_argument("--job-title", required=True)
    add_parser.add_argument("--candidate-name")
    add_parser.add_argument("--level", default="应届/初级")
    add_parser.add_argument("--city", default="")
    add_parser.add_argument("--company-model", default="")
    add_parser.set_defaults(func=command_add)

    stage_parser = subparsers.add_parser("set-stage", help="更新一个案例的阶段状态")
    stage_parser.add_argument("manifest")
    stage_parser.add_argument("case_id")
    stage_parser.add_argument("stage", choices=tuple(dict.fromkeys((*STAGES, *GUIDE_STAGES))))
    stage_parser.add_argument("state", choices=sorted(STAGE_STATES))
    stage_parser.add_argument("--note", default="")
    stage_parser.set_defaults(func=command_set_stage)

    evidence_parser = subparsers.add_parser(
        "set-evidence", help="更新实践证据状态并自动派生简历准入"
    )
    evidence_parser.add_argument("manifest")
    evidence_parser.add_argument("case_id")
    evidence_parser.add_argument("state", choices=sorted(PRACTICE_STATES))
    evidence_parser.add_argument("--evidence", action="append", default=[])
    evidence_parser.add_argument(
        "--resource-dependency",
        choices=("low", "medium", "high"),
    )
    evidence_parser.add_argument("--non-substitutable-gap")
    evidence_parser.add_argument("--note", default="")
    evidence_parser.set_defaults(func=command_set_evidence)

    validate_parser = subparsers.add_parser("validate", help="校验结构、来源和产物")
    validate_parser.add_argument("manifest")
    validate_parser.add_argument("--check-files", action="store_true")
    validate_parser.set_defaults(func=command_validate)

    summary_parser = subparsers.add_parser("summary", help="汇总批次与阶段进度")
    summary_parser.add_argument("manifest")
    summary_parser.set_defaults(func=command_summary)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
