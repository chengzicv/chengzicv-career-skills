# 产品 Runtime 集成契约

## 一句话职责

平台保存状态，Skill 生成行为；Evidence Pack 在面试完成后一次性产生，只服务报告。

## 平台必须持有

- `session_id`
- 简历、JD、岗位与公司信息
- 完整原始 `messages`，每条有稳定 `message_id`
- `current_question_id`
- `followup_count`
- `completed_question_ids`
- `onboarding_version_seen`
- `skill_version`
- 面试、提证、诊断每次调用的 run 记录

## 推荐调用

### 面试调用

每轮传入材料、session state、完整 transcript（五题 MVP 可全量传入）和当前回答。模型返回 `interview-turn`。平台保存模型消息并更新题号/追问计数。

不要在此阶段生成 Evidence Pack。

### 提证调用

五题完成后，使用完整 transcript 发起一次独立调用，生成 Evidence Pack。运行逐字校验；失败时带校验错误重试，最多两次。

### 诊断调用

使用一次新调用，传入材料、完整 transcript、已校验 Evidence Pack 和评分规则。生成报告后运行 Schema 与 evidence_ref 校验。

## 恢复

恢复只依赖平台的 messages 和 session state。若面试未完成，从未完成题继续；若面试完成而报告缺失，重新执行提证和诊断。

## 失败与幂等

- 所有 run 带幂等键，重试不重复推进题号。
- 原始消息写入成功后才调用模型。
- 模型响应保存成功后再向前端确认完成。
- Evidence Pack 校验持续失败时，诊断回退为完整 transcript，并在报告中不展示无法核验的直接引用。
- 诊断失败不影响已保存的面试历史。

## 不要做

- 不依赖模型厂商 thread 作为唯一事实源。
- 不让 Skill 声称自己保存了聊天。
- 不用自由摘要替代原始 transcript。
- 不把 Evidence Pack 当作暂停恢复状态。
