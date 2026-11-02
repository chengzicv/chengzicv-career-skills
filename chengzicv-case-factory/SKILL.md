---
name: chengzicv-case-factory
description: 为指定岗位与职级生成独立披露的虚拟简历及岗位入门。虚拟简历的写法、结构、个人优势、篇幅、标点和事实纪律全部沿用 chengzicv-resume；本 Skill 只负责虚拟案例设定、岗位研究、岗位入门与批次生产。
disable-model-invocation: true
---

# ChengziCV Case Factory

> **套件启动**：开始任何工作前，先读取并执行 `../chengzicv/references/suite-bootstrap.md`（共享工作区、档案恢复、产物落盘、事实边界）。

本 Skill 产出**虚拟简历＋岗位入门**，让读者看懂工作在做什么、是否愿意继续了解，也看见相关经历怎样呈现判断与执行深度。

## 唯一简历标准

本 Skill 不维护第二套简历标准。生成或改写虚拟简历前，必须先读取并执行：

- `../chengzicv-resume/SKILL.md`
- `../chengzicv-resume/references/plainspoken-resume-style.md`
- `../chengzicv-resume/references/advantage-block.md`
- `../chengzicv-resume/references/evidence-safeguard.md`
- `../chengzicv-resume/references/one-page-markdown-rules.md`

按任务需要再读：

- 有 JD 或要做关键词对齐：`../chengzicv-resume/references/dynamic-jd-ats-engine.md`
- 技术、工程岗需要机制深度：`../chengzicv-resume/references/technical-evidence.md`
- 需要真实 offer 标尺：`../chengzicv-resume/references/real-offer-benchmarks.md`
- 需要完整结构示范：`../chengzicv-resume/references/exemplar-benchmark.md`

以上文件是简历正文、个人优势、经历结构、篇幅、加粗、标点、事实边界和自检的唯一标准。本 Skill 的参考文件只补充虚拟案例特有的设定与生产规则；冲突时以 resume-latest 为准。

## 本 Skill 负责什么

- 设计虚拟人物、公司、项目、时间、职责、数字和完成状态，支撑目标岗位与职级。
- 研究公开 JD、行业流程、法规和专业约束，校准岗位入口与工作内容。
- 把同一套虚拟事实写成两份材料：一份虚拟简历，一篇岗位入门。
- 维护批次清单、逐岗审核和产物路径。

不负责：真人简历诊断、冲高候选补全、ATS 核对报告、面试小抄；真人材料与这些产物转 `chengzicv-resume`。真实 offer 标尺只在需要时读取 resume-latest 的 reference，本 Skill 不维护。

## 默认交付

每岗两份产物：

- `01-岗位标杆虚拟简历`：按 resume-latest 的标准写，不另设格式；成稿按 `../chengzicv-resume/assets/resume-document-template.html` 渲染 HTML，并保留 `.md` 源稿。
- `03-岗位入门.md`：按本 Skill 的 `references/user-case-pack.md`、`references/gold-standard.md` 写，属编辑管线稿件，保持 Markdown。

虚拟简历只加四类案例特有处理：

- 独立文件顶部保留一次案例说明；平台展示由平台统一说明。
- 人物默认小橙；姓名、学校、公司、任职、客户、奖项和数据全部虚拟化。
- 不默认输出真人流程的追问清单、候选补全台账、ATS 报告、冲高版或小抄；用户明确要求时按 resume-latest 的对应规则追加。虚拟事实在 `_内部` 的 `scenario_facts` 锁定。
- 简历与岗位入门共用同一事实底稿，姓名、公司、时间、职责、数字和进展一致。

## 使用顺序

1. 读 `references/product-boundary.md`、`references/virtual-case-design.md`、`references/virtual-experience-design.md`，确定披露、案例模式和事实边界。
2. 按 `references/production-contract.md` 研究公开 JD 和专业约束；批量时读 `references/batch-planning.md`。
3. 先记录用户指定的岗位、职级、经历数量、必含方向、格式和篇幅；按 `references/virtual-case-design.md` 建共享事实。
3.5. 专业深浅有争议时读 `references/depth-calibration.md`，按目标职级和真实 JD 校准；技术写法本身按 resume-latest 的 `technical-evidence.md`，本 Skill 不另设技术写作标准。
4. 写虚拟简历：按「唯一简历标准」执行，不套用本 Skill 的旧三段式、旧范文或旧版式。
5. 写岗位入门：按 `references/user-case-pack.md` 与 `references/gold-standard.md`。
6. 按 `references/quality-gates.md` 检查；批次进度按 `references/manifest-schema.md`。

## 虚拟案例设计

- **模式**：用户已有专业或项目、但想看虚拟标杆时，用「基于用户骨架」；用户只要行业标准示例，或现有主题离岗位太远时，用「岗位原生」。两种模式都必须虚拟化姓名、学校、公司、任职、客户、数据和奖项。
- **深度**：经历要有需求、约束、判断、动作、证据、结果和复盘；技术案例保留工作范围、实现机制、版本演进和交付证据。具体设计维度见 `references/virtual-case-design.md` 和 `references/virtual-experience-design.md`。
- **职责边界**：初级以执行、核对、记录、协作为主，不包办审批、质量放行、客户承诺、法规签字；资深可以承担方案、核心实现、评审和迁移，但依 JD 和设定，不自动授予行政权力。
- **数字**：先算清分子、分母、时间窗、样本和口径，再写进两份材料；保留代价、未完成项和仍未解决的问题，不强制每个项目有失败或提升率。
- **隔离**：不复制真实公司、真实人物、真实客户、真实奖项或真实业绩；公开 JD 只支持岗位尺度，不支持虚拟业绩。虚拟事实不得进入真人档案或真实简历。

## 岗位文章写法

用任务和材料开场，角色对话只交代事情。保留少量可观察的记录和一个轻量判断，解释为什么处理、用什么处理、交给谁。工具随工作需要出现，不逐项塞入飞书、AI和开会。

短小具体的小标题帮助浏览；术语随任务解释。工作感受、相近岗位比较和入门建议回到前面的动作，不根据性格标签或一次练习判定适配。说明同名职位也可能有不同职责。文章以讲清楚为准，不固定字数、标题数量，也不扩成完整操作手册。

公开事实就近附来源；人物、对话、经营和工作数字在内部标为情境设定，不冒充真实采访、研究或业绩。跨多日写清跨度，计划不写成完成，前后变化不当作因果证明。

## 展示与协作

- 简历正文的展示、标点、篇幅和自检按 resume-latest；本 Skill 不再重复。
- 岗位入门正文不出现 Manifest、CASE-ID、证据状态码或制作旁白；业务约束、数字口径和进展限制仍要讲清。
- 首次调用用一句话说明交付后开始，不背诵介绍，不要求用户再次提供已有岗位、素材或确认稿。
- 批次默认先建目录与计划，一次完成一岗的两份材料，用户 check 通过再进入下一岗；用户已明确授权连续生产时按其要求。自查完成不等于用户认可，修改意见先落实到当前岗。
- 局部修改保留用户内容；大幅重做另存版本，明确当前审核稿。交付两份 MD 链接和简短说明，不额外给生产报告。仅在用户明确要求时外部发布。
