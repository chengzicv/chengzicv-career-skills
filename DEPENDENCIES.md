# ChengziCV 依赖审计

## 结论

公开用户运行包由 `chengzicv` 总入口、九个面向求职者的执行 Skill 和 `chengzicv-update` 更新入口组成。ChengziCV 之间可以路由；核心执行方法不依赖本机其他 Skill。内部 To B 的 `chengzicv-light-business-intake` 不进入公开包。

| Skill | 套件内关系 | 外部运行条件 | 无条件时的回退 |
| --- | --- | --- | --- |
| `chengzicv` | 路由到九个公开执行 Skill | 无 | 目标成员缺失时说明缺少哪个安装包 |
| `chengzicv-profile` | 可交接到职业、简历或面试入口 | 文件持久化取决于宿主能力和用户授权 | 普通聊天交付可复制档案快照，不承诺跨会话自动记忆 |
| `chengzicv-career` | 可交接到简历或面试入口 | 时效性事实需要联网 | 请求用户提供 JD 或材料，并降低结论范围 |
| `chengzicv-resume` | 可交接到职业与面试入口 | 飞书自动发布可用官方 `lark-cli` | 先交付本地 Markdown 与素材目录，提供网页导入路径 |
| `chengzicv-job-greeting` | 承接简历和 JD，生成招聘平台开场、推进与跟进话术 | 无；正式邮件求职信不属于本 Skill | 没有单个 JD 时按已锁定岗位方向给基础版，并明确不是单岗定制稿 |
| `chengzicv-interview-prep` | 可承接简历并交接到初筛、专项或复盘 | 时效性研究需要联网；云文档发布可选用对应平台工具 | 仍可交付本地双文档、来源、Mermaid 与 SVG；不把未发布稿说成在线文档 |
| `chengzicv-interview-mock` | 可交接到专项、简历或复盘 | Python 仅在运行确定性校验脚本时需要 | 校验器只使用 Python 标准库，无第三方包 |
| `chengzicv-interview-practice` | 可交接到简历、初筛或复盘 | 网页搜索和代码工具均为可选 | 继续训练并明确降低时效性判断置信度 |
| `chengzicv-interview-review` | 按复盘证据回补其他入口 | 音视频转写能力视宿主环境而定 | 只请求一次逐字稿，不假装已读取音视频 |
| `chengzicv-case-factory` | 独立生成虚拟简历和岗位入门案例，可作为职业了解与简历深度参考 | 时效性岗位事实需要联网；Markdown 为默认交付 | 无法联网时只基于用户材料与已有知识生成，并标记待核验事实 |
| `chengzicv-update` | 只更新并重新同步官方 ChengziCV Skills | 需要宿主能够执行终端命令 | 无终端能力时提示用户重新下载公开安装包 |

## 已消除的隐藏依赖

- 飞书作品集规范不再读取 `jc-markdown-visual-writer`，需要的简单图示规则已经内聚。
- 职业规划不再点名或调用非 ChengziCV 的 Offer Skill。
- 面试模拟与复盘校验脚本不再要求额外安装 `jsonschema`。
- 产品 Skill 中的 Evals 已移到本开发仓库，不进入普通运行时路由。
- 零材料建档的模板与隐私规则已内聚在 `chengzicv-profile`，不依赖作者本机示范简历或 FlowUs 页面。
- 面试前准备的核心研究与双文档交付不依赖 `jc-rich-doc-publisher`；该 Skill 只在同机可用且用户明确要求云文档时增强平台排版、协作和校验。

## 飞书的特殊性

`lark-cli` 是外部工具，不是另一个 Skill 依赖。自动发布时先检测；缺失时说明官方来源并取得用户同意后安装。配置和 OAuth 必须由用户在飞书页面确认，Agent 负责生成链接与二维码、等待用户回来后继续验证和发布。用户不安装时仍能得到本地双文档和手工导入路径。
