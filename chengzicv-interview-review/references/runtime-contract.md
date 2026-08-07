# 产品 Runtime 集成契约

## 一句话职责

平台保存原始材料和任务状态，Skill 生成 Evidence Pack、诊断报告与面经拆解产物。

## 平台必须持有

- `session_id`
- 任务模式：`diagnosis_report | interview_experience_deconstruction | full_review`
- 可选的简历、JD、岗位与公司信息
- 完整原始 `messages`，每条有稳定 `message_id`
- Evidence Pack、诊断报告和面经拆解的完成状态
- `skill_version`
- 提证、诊断与面经拆解每次调用的 run 记录

## 推荐调用

### 提证调用

使用完整 transcript 发起一次独立调用，生成 Evidence Pack。运行逐字校验；失败时带校验错误重试，最多两次。

### 诊断调用

使用一次新调用，传入材料、完整 transcript、已校验 Evidence Pack 和评分规则。生成报告后运行 Schema 与 `evidence_ref` 校验。

### 面经拆解调用

使用完整 transcript 发起独立调用。产物必须覆盖全部有诊断价值的问答组，不预设固定题数。

`full_review` 先执行提证和诊断，再复用同一份完整 transcript 执行面经拆解。

## 恢复

恢复依赖平台保存的原始 messages 和任务状态：

- Evidence Pack 缺失时重新提证；
- Evidence Pack 已校验但报告缺失时直接诊断；
- 诊断报告存在但面经拆解缺失时直接拆解；
- 已完成产物不重复生成，除非用户明确要求重做。

## 失败与幂等

- 所有 run 带幂等键，重试不重复写入同一产物。
- 原始消息写入成功后才调用模型。
- 模型响应保存成功后再向前端确认完成。
- Evidence Pack 校验持续失败时，诊断回退为完整 transcript，并在报告中不展示无法核验的直接引用。
- 某一产物生成失败不影响已经保存的其他产物和原始 transcript。

## 不要做

- 不依赖模型厂商 thread 作为唯一事实源。
- 不让 Skill 声称自己保存了聊天。
- 不用自由摘要替代原始 transcript。
- 不把 Evidence Pack 当作暂停恢复状态。

