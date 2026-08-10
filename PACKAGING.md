# ChengziCV 发布包边界

## 用户安装包

每个 Skill 只分发运行时会使用的内容：

- `SKILL.md` 与 `agents/openai.yaml`；
- 首次使用的 `onboarding/`；
- 按条件读取的 `references/`；
- 确定性校验所需的 `scripts/`、`schemas/`、`runtime/`、`scorecards/` 与 `prompts/`；
- 实际产物需要复制的 Assets；`chengzicv-profile` 分发候选人档案与零材料简历两份 Markdown 模板。

## 开发仓库

以下内容不放进单个用户 Skill：

- `evals/` 中的触发、回归和端到端评测；
- 依赖审计、发布清单和设计记录；
- 历史基准输出与测试报告。
- `.DS_Store`、缓存目录、临时转写和本地生成物。

Gotcha 和质量红线不是因为使用英文名就要单独分发。已经被真实失败证明、会改变 Agent 行为的规则，应编译进 `SKILL.md` 或对应 Reference；测试这些规则的案例留在开发仓库。这样既能稳定不同模型，又不会让用户包携带运行时从不读取的维护文档。
