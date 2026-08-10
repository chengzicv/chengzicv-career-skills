# ChengziCV 依赖审计

## 结论

用户运行包由 `chengzicv` 总入口和五个执行 Skill 组成。ChengziCV 之间可以路由；执行方法不依赖本机其他 Skill。

| Skill | 套件内关系 | 外部运行条件 | 无条件时的回退 |
| --- | --- | --- | --- |
| `chengzicv` | 路由到五个子 Skill | 无 | 目标成员缺失时说明缺少哪个安装包 |
| `chengzicv-career` | 可交接到简历或面试入口 | 时效性事实需要联网 | 请求用户提供 JD 或材料，并降低结论范围 |
| `chengzicv-resume` | 可交接到职业与面试入口 | 飞书自动发布可用官方 `lark-cli` | 先交付本地 Markdown 与素材目录，提供网页导入路径 |
| `chengzicv-interview-mock` | 可交接到专项、简历或复盘 | Python 仅在运行确定性校验脚本时需要 | 校验器只使用 Python 标准库，无第三方包 |
| `chengzicv-interview-practice` | 可交接到简历、初筛或复盘 | 网页搜索和代码工具均为可选 | 继续训练并明确降低时效性判断置信度 |
| `chengzicv-interview-review` | 按复盘证据回补其他入口 | 音视频转写能力视宿主环境而定 | 只请求一次逐字稿，不假装已读取音视频 |

## 已消除的隐藏依赖

- 飞书作品集规范不再读取 `jc-markdown-visual-writer`，需要的简单图示规则已经内聚。
- 职业规划不再点名或调用非 ChengziCV 的 Offer Skill。
- 面试模拟与复盘校验脚本不再要求额外安装 `jsonschema`。
- 产品 Skill 中的 Evals 已移到本开发仓库，不进入普通运行时路由。

## 飞书的特殊性

`lark-cli` 是外部工具，不是另一个 Skill 依赖。自动发布时先检测；缺失时说明官方来源并取得用户同意后安装。配置和 OAuth 必须由用户在飞书页面确认，Agent 负责生成链接与二维码、等待用户回来后继续验证和发布。用户不安装时仍能得到本地双文档和手工导入路径。

