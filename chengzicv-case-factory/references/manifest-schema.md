# 双交付批次与旧模式兼容

## 当前新批次

保留 `delivery_mode=job_guide`、`schema_version=1.2` 兼容层，用显式 `required_deliverables` 声明当前默认的虚拟简历与岗位入门。不要为了文件数量更换旧批次模式或恢复四件套。

```text
批次/
  _内部/manifest.json
  供应链专员/01-岗位标杆虚拟简历.md
  供应链专员/03-岗位入门.md
```

单岗编辑不强制创建清单。清单位于内部目录，路径相对清单所在目录；展示正文不含内部字段。默认小橙，平台统一展示案例属性。

## 最小结构

```json
{
  "schema_version": "1.2",
  "delivery_mode": "job_guide",
  "batch_id": "career-cases-01",
  "interpretation": "pairs",
  "expected_case_count": 1,
  "default_candidate_name": "小橙",
  "presentation": {"disclosure_location": "platform"},
  "required_deliverables": ["job_guide", "virtual_resume"],
  "workflow": {
    "mode": "sequential_user_review",
    "require_explicit_user_approval_before_next": true
  },
  "cases": [
    {
      "case_id": "CASE-001",
      "industry": "生活用品品牌",
      "job_title": "供应链专员",
      "candidate_name": "小橙",
      "level": "应届/初级",
      "city": "",
      "company_model": "品牌公司订单与库存协同",
      "status": "in_progress",
      "stages": {
        "selection": "complete",
        "research": "pending",
        "job_guide": "pending",
        "audit": "pending"
      },
      "adaptation": {"reference_status": "reference_only", "resume_eligible": false},
      "sources": [],
      "outputs": {},
      "additional_deliverables": {
        "virtual_resume": {"status": "pending", "path": ""}
      },
      "user_review": {"status": "pending", "approved": false},
      "blocked_reason": "",
      "notes": []
    }
  ]
}
```

来源包含 category、title、url、accessed_at、used_for；有可靠发布日期才加 published_at。research 完成至少有一条 job 来源；工具、产品、专业约束按需要补充。虚拟人物、工作和经营数据在 scenario_facts 或 virtual_candidate_profile 等内部字段单独记载，不能把 JD 当成经营结果的证据。

## 两份文件与审核

文章写完登记 `outputs.job_guide`；简历写完登记 `additional_deliverables.virtual_resume.path`，并将其 status 设为 complete。路径示例：

```json
{
  "outputs": {"job_guide": "../供应链专员/03-岗位入门.md"},
  "additional_deliverables": {
    "virtual_resume": {
      "status": "complete",
      "path": "../供应链专员/01-岗位标杆虚拟简历.md"
    }
  }
}
```

`outputs` 保留旧兼容约定，仅接收 job_guide。简历不再是可漏掉的附件：声明 virtual_resume 为必交时，audit 完成前它必须已完成且路径有效。`validate --check-files` 同时核对两份文件存在、Markdown层次、制作旁白以及路径是否重复。

阶段仍为 selection、research、job_guide、audit；不跳过必需阶段。所有阶段 complete 表示制作自查完成，**不表示用户认可**。只有用户明确通过当前岗后，才记录 `user_review.status=approved`、`approved=true`；可以加审批消息摘要，不能由自动审查伪造。

逐岗模式按 cases 顺序检查：前序岗位未得到用户确认，后续岗位不能进入 research 或写作。用户明确授权连续生产时，将 workflow.mode 记录为 continuous_authorized 并注明授权依据；不得为了通过检查而改变模式。

## 命令

```bash
python3 scripts/case_manifest.py init /项目/_内部/manifest.json \
  --batch-id career-cases-01 --expected-count 2
python3 scripts/case_manifest.py add /项目/_内部/manifest.json \
  --case-id CASE-001 --industry 生活用品品牌 --job-title 供应链专员
```

补入公开 sources，再标记 research complete。两份文件完成后登记路径与简历状态，依次执行：

```bash
python3 scripts/case_manifest.py set-stage /项目/_内部/manifest.json CASE-001 research complete
python3 scripts/case_manifest.py set-stage /项目/_内部/manifest.json CASE-001 job_guide complete
python3 scripts/case_manifest.py set-stage /项目/_内部/manifest.json CASE-001 audit complete
python3 scripts/case_manifest.py validate /项目/_内部/manifest.json --check-files
python3 scripts/case_manifest.py summary /项目/_内部/manifest.json
```

用户明确只要文章时，init 加 `--job-guide-only`；不可为了避免写简历而默认使用该参数。用户只要单份简历时按单岗文件处理，不强造文章批次。

## 兼容与展示

- 旧1.2清单未声明 required_deliverables 或 user_requested_deliverables 时，仍按单文章处理，不自动要求补简历。
- 已有混合批次的 user_requested_deliverables 可作为兼容声明，additional_deliverables 中的简历会被核对。新批次优先用 required_deliverables。
- 已有1.1或明确指定 legacy_deep 的清单沿用旧检查；只在继续此类批次时读 `legacy-manifest-schema.md`。
- reference_only、resume_eligible=false 表示这些仍是虚拟案例，不能通过 set-evidence 变成个人经历。
- 平台模式不重复标注案例性质；明确独立外发时用 document 模式，在每个独立文件开头简短说明一次。

脚本不判断 STAR 写得好不好、岗位是否真实、数字是否有业务意义，也不替代来源核对。先按 quality-gates 做内容检查，再记录完成；不自动发布、不自动进入下一岗。
