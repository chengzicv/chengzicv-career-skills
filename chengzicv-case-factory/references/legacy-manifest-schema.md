# 仅供旧版深度批次兼容

本文件不定义当前默认产物。新文章使用 job_guide 模式；这里的四件套、证据状态和披露要求仅适用于已有 1.1 批次或明确要求的 legacy_deep 模式。

# 批次 Manifest 与断点续跑

## 何时读取

创建新批次、继续历史批次、更新案例阶段、检查产物完整性或汇总进度时读取。

## 一、保存位置

Manifest 属于用户项目数据，放在本次交付目录，不能写进 Skill 源目录。默认使用 JSON，文件名可采用：

```text
案例批次-{batch_id}-manifest.json
```

若当前项目有文件命名和目录规则，优先服从项目规则。Manifest 中使用相对路径引用产物，移动整个批次目录后仍应可验证。

## 二、最小结构

```json
{
  "schema_version": "1.1",
  "batch_id": "2026-consumer-jobs-01",
  "interpretation": "pairs",
  "expected_case_count": 50,
  "default_candidate_name": "小橙",
  "created_at": "2026-08-27T00:00:00+08:00",
  "updated_at": "2026-08-27T00:00:00+08:00",
  "cases": [
    {
      "case_id": "CASE-001",
      "industry": "食品饮料",
      "job_title": "商品开发专员",
      "candidate_name": "小橙",
      "level": "应届/初级",
      "city": "深圳",
      "company_model": "自有品牌+OEM",
      "status": "in_progress",
      "stages": {
        "selection": "complete",
        "research": "pending",
        "company_model": "pending",
        "resume": "pending",
        "portfolio": "pending",
        "interview_handbook": "pending",
        "student_practice": "pending",
        "audit": "pending"
      },
      "uniqueness": {
        "business_trigger": "",
        "primary_constraint": "",
        "failure_type": "",
        "stop_decision": "",
        "evidence_form": ""
      },
      "adaptation": {
        "reference_status": "reference_only",
        "evidence_state": "reference_only",
        "resume_eligible": false,
        "resource_dependency": "unassessed",
        "non_substitutable_gap": "",
        "evidence_basis": [],
        "reference_only_entities": []
      },
      "sources": [],
      "outputs": {},
      "blocked_reason": "",
      "notes": []
    }
  ]
}
```

`interpretation` 允许：`pairs`、`cartesian`、`custom`。`expected_case_count` 是批次目标，不要求规划第一分钟就已经填满；校验器会在数量不一致时给警告。

## 三、阶段状态

阶段状态只使用：

```text
pending / in_progress / complete / blocked / skipped
```

案例总状态只使用：

```text
planned / in_progress / complete / blocked
```

更新顺序：先写本阶段产物或阻塞证据，再更新阶段状态和 `updated_at`。不要先标 `complete` 再补文件。

`audit=complete` 且其余必需阶段完成后，案例才能标记为 `complete`。用户明确缩小交付范围时，相应阶段可标为 `skipped`，并在 `notes` 写明授权范围。

`student_practice` 表示“可执行实践包已经设计完成”，不表示学生已经执行，更不表示可以写进简历。教学参考案例不制作实践包时可标为 `skipped`；制作实践包后，初始状态仍必须是 `practice_ready`、`resume_eligible=false`。

## 四、实践状态与简历准入

每个案例必须包含 `adaptation`：

```json
{
  "reference_status": "reference_only",
  "evidence_state": "practice_ready",
  "resume_eligible": false,
  "resource_dependency": "medium",
  "non_substitutable_gap": "没有真实客户系统、上线权限与客户签字，不能声称实施上线。",
  "evidence_basis": [],
  "reference_only_entities": ["案例公司名称", "案例学校名称", "案例比赛名称", "案例候选人名称"]
}
```

`reference_status` 固定为 `reference_only`。`evidence_state` 只允许：

```text
reference_only / practice_ready / executed_unverified /
evidence_verified / real_experience_verified
```

只有 `evidence_verified` 与 `real_experience_verified` 可以令 `resume_eligible=true`；其余状态必须为 `false`。`resource_dependency` 允许 `unassessed / low / medium / high`，但进入 `practice_ready` 后不能继续使用 `unassessed`。高资源实践必须填写 `non_substitutable_gap`。已经执行或验证时，`evidence_basis` 不能是空数组。

制作学生实践包时，`reference_only_entities` 必须登记教学参考中的候选人、公司、学校和比赛名称；启用文件校验后，任何一个名称进入任务包、证据模板或起始数据都会报错。这样不能只靠写作提示维持隔离。

## 五、来源记录

每条来源至少包含：

```json
{
  "category": "job",
  "title": "岗位页面标题",
  "url": "https://example.com/job",
  "published_at": "",
  "accessed_at": "2026-08-27",
  "used_for": "确认岗位Title、职责和协作对象"
}
```

深度案例研究完成时，至少覆盖：

- `product`：真实产品或商业形态；
- `constraint`：法规、平台、质量或专业约束；
- `job`：真实岗位要求。

找不到发布日期时保留空值并记录访问日期，不编日期。

## 六、产物记录

`outputs` 使用固定键：

```json
{
  "research_design": "案例-CASE-001-食品饮料-商品开发专员-调研与设计说明.md",
  "resume": "案例-CASE-001-食品饮料-商品开发专员-示例简历.md",
  "portfolio": "案例-CASE-001-食品饮料-商品开发专员-工作样本.md",
  "interview_handbook": "案例-CASE-001-食品饮料-商品开发专员-面试教学手册.md",
  "student_practice_pack": "案例-CASE-001-学生实践任务包.md",
  "evidence_template": "案例-CASE-001-实践记录与证据模板.md",
  "starter_data": "案例-CASE-001-教学起始数据.csv"
}
```

文件名必须包含案例 ID，并用“案例”或“示例”表明材料属性。启用 `--check-files` 时，校验器还会检查文件开头是否存在“教学示例、教学案例、教学材料、非真实候选人”或兼容的旧版“虚拟案例”披露。如果文件被人工修改，续跑时先读取并保留人工内容；不要因模板升级整体覆盖。

`student_practice=complete` 时，后三项为必需产物。任务包和证据模板开头必须同时披露 `practice_ready` 与 `resume_eligible=false`。起始数据只能提供输入、约束或故意留待学生识别的问题，不能预填学生的决策、偏差、结论或成果。教学参考中的虚构公司、比赛、学校、客户和业绩不得移植到学生实践包。

## 七、脚本

使用标准库脚本：

```bash
python3 scripts/case_manifest.py init MANIFEST \
  --batch-id consumer-jobs-01 \
  --expected-count 50 \
  --delivery-mode legacy_deep

python3 scripts/case_manifest.py add MANIFEST \
  --case-id CASE-001 \
  --industry 食品饮料 \
  --job-title 商品开发专员 \
  --level 应届/初级

python3 scripts/case_manifest.py set-stage MANIFEST CASE-001 research complete
python3 scripts/case_manifest.py set-evidence MANIFEST CASE-001 practice_ready \
  --resource-dependency low
python3 scripts/case_manifest.py set-evidence MANIFEST CASE-001 executed_unverified \
  --evidence 学生交付/CASE-001/执行日志.md \
  --evidence 学生交付/CASE-001/分析底稿.xlsx
python3 scripts/case_manifest.py set-evidence MANIFEST CASE-001 evidence_verified \
  --evidence 学生交付/CASE-001/核验记录.md
python3 scripts/case_manifest.py validate MANIFEST --check-files
python3 scripts/case_manifest.py summary MANIFEST
```

`set-evidence` 自动派生 `resume_eligible`，不能用命令手工绕过：只有两个 verified 状态会变为 `true`。高资源实践进入 `practice_ready` 时需同时提供 `--non-substitutable-gap`。`init` 不覆盖已有文件。脚本只做结构、状态、重复组合、来源类别和产物路径等确定性检查，不代替人工核验行业研究质量、证据真实性或简历内容深度。

## 八、续跑顺序

1. 读取 Manifest；
2. 运行 `validate`；
3. 处理结构错误、丢失文件和人工修改冲突；
4. 汇总未完成或阻塞案例；
5. 从最早未完成阶段继续；
6. 完成后更新该案例，不改无关案例；
7. 每批结束运行 `summary` 和批次质量门。
