# ChengziCV Career Skills

> 一组面向中文求职场景的 Agent Skills：从简历整理、专项深挖、初筛模拟到真实面试复盘，让建议尽量回到候选人的原始材料和现场回答。

这套工具包含 4 个可以独立使用的 Skill。你不需要先理解内部方法，只要提供简历、JD 或面试记录，再选择与当前任务最接近的入口。

## 这套 Skills 能帮你完成什么？

它覆盖求职准备中四个彼此不同、又能自然衔接的任务。

| 你的任务 | 使用的 Skill | 你会得到 |
| --- | --- | --- |
| 整理或改写简历与配套材料 | `chengzicv-resume-mentor` | 基于已有事实的可投递简历，以及按需生成的 STAR 素材、项目手册或作品集 |
| 针对项目、岗位知识或业务 Case 连续深挖 | `chengzicv-interview-drill` | 动态专项面试、分支反馈、必要教学与无提示复测 |
| 完成一场五题左右的企业初筛模拟 | `chengzicv-interview-diagnosis` | 基于候选人原话的证据包、企业视角诊断与短时复练任务 |
| 复盘已经发生的真实面试 | `chengzicv-interview-review` | 逐字稿证据诊断、完整面经拆解与参考高分答法 |

## 我现在该选哪个入口？

有简历要改，先用 Resume Mentor；要练专项能力，用 Deep-Dive Interviewer；要模拟 HR 或综合初筛，用 Screening Interviewer；已经面完并有录音或逐字稿，用 Interview Review。

```text
简历、JD、项目材料
├── 想先把材料改得具体可信 → chengzicv-resume-mentor
├── 想围绕项目或岗位能力连续深挖 → chengzicv-interview-drill
└── 想做一场短初筛模拟 → chengzicv-interview-diagnosis

已有面试录音、视频或逐字稿
└── 想诊断表现并整理面经 → chengzicv-interview-review
```

四个 Skill 不要求按固定顺序使用。只有当前任务需要时，直接调用对应入口即可。

## 快速开始

将仓库中的 4 个 Skill 目录安装到支持 Agent Skills 的工具中。不同工具的安装位置和调用语法可能不同，请以对应产品文档为准。

如果仓库发布到 GitHub，也可以使用通用 Skills 安装器：

```bash
npx -y skills add chengzicv/chengzicv-career-skills -g --all
```

安装后，可以直接这样描述任务：

```text
使用 chengzicv-resume-mentor，根据这份简历和 JD 给我一版可投递快稿。

使用 chengzicv-interview-drill，针对我的项目连续深挖；先考后教。

使用 chengzicv-interview-diagnosis，根据我的简历开始一场企业初筛模拟。

使用 chengzicv-interview-review，复盘这份面试逐字稿，并整理完整面经。
```

## 它怎样避免把建议写成“AI 编的经历”？

四个 Skill 共用一条事实边界：候选人的经历、数字、结果和个人贡献，只能来自候选人提供的材料或现场回答。

- 简历改写会区分真实事实、待确认信息和虚拟教学案例。
- 模拟面试会把采集证据与生成诊断分开，重要判断需要回到候选人原话。
- 专项训练会区分经历证据、专业正确性和表达质量，不把“没问到”直接判成能力不足。
- 真实面试复盘会区分原项目事实与通用参考方案，避免把参考答案倒灌成候选人经历。

## 隐私数据会保存到哪里？

这些 Skill 本身不内置真实候选人数据，也不负责跨会话持久化。普通聊天模式只使用当前对话中可见的材料；产品集成模式下，简历、录音、逐字稿和报告如何存储，由宿主产品负责。

求职材料通常包含姓名、电话、邮箱、教育经历和工作记录。使用前请确认宿主产品的数据政策，不要把未脱敏的候选人材料提交到不受信任的服务，也不要把真实面试记录直接提交到公开 issue、公开日志或示例文件中。

## 使用边界

- 这是候选人训练与材料整理工具，不代表任何企业的内部录用标准。
- 不输出录用概率，也不承诺使用后一定通过面试。
- 不依据性别、年龄、籍贯、婚育、健康、民族、宗教或政治倾向作负面判断。
- 初筛模拟不替代算法、编码、系统设计或岗位专家 Case。
- 涉及时效性规则、法律、财税、平台政策或其他高风险专业判断时，应先核验可靠来源。
- AI 生成内容仍需人工核对，尤其是数字、个人贡献、技术实现和可外发材料。

## 版本怎么管理？

Skill 的目录名和调用名保持稳定，不把 `v1`、`v2` 写进名称。日常变化由 Git commit 记录，对外发布使用仓库级语义化版本和 Git tag，例如 `v1.0.0`、`v1.1.0`、`v2.0.0`。

- 修正文案、示例或不改变使用方式的缺陷：patch。
- 增加向后兼容的能力：minor。
- 修改触发方式、输入输出或关键行为边界：major。

Runtime JSON 等机器契约可以保留独立的 `schema_version` 或 `skill_version`。它们用于兼容性校验，不属于 Skill 的公开名称。

## 项目结构

```text
.
├── chengzicv-resume-mentor/
├── chengzicv-interview-drill/
├── chengzicv-interview-diagnosis/
├── chengzicv-interview-review/
└── README.md
```

每个目录中的 `SKILL.md` 定义触发条件和核心工作流；`references/` 保存按需加载的方法与模板；`scripts/`、`schemas/` 和 `runtime/` 只在对应 Skill 需要确定性校验或产品集成时使用。

## 许可证

本项目采用 [MIT License](LICENSE)。
