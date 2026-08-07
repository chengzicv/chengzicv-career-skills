# ChengziCV Career Skills

> 4 个面向中文求职场景的 Agent Skills：改简历、练专项面试、做初筛模拟、复盘真实面试。

每个 Skill 都可以单独使用。把手头的简历、JD、项目材料或面试记录交给对应入口，就能直接开始。

## 为什么值得用这套 Skills？

它解决的不是“帮我把话写漂亮”，而是三个更难的问题：**哪些经历是真的、目标岗位在意什么、下一次怎样答得更稳。**

- **不替你编经历**：数字、结果、个人贡献和技术实现都要能回到你的材料或回答。
- **先给可用结果，再补关键证据**：简历材料足够时先出能投的版本，不用先回答一长串问题。
- **一次只处理一个问题**：减少同时组织多段答案的压力，也让追问能跟着你的真实回答变化。
- **不只点评，还会复练**：专项训练遵循“先考—反馈—讲解—重答—变式复测”，直到确认你真的会了。
- **诊断可以追溯**：模拟面试和真实面试复盘尽量引用原话；没有问到的能力只标记为证据不足，不直接判低分。
- **四个入口彼此独立**：只改简历、只练一场面试或只复盘一份录音都可以，不必走完整套流程。

## 它和普通求职提示词有什么不同？

普通提示词通常追求“一次生成一份看起来不错的答案”；这套 Skills 更重视结果能不能被候选人解释、被面试官继续追问。

| 常见做法 | ChengziCV 的做法 |
| --- | --- |
| 根据职位描述补出一套漂亮经历 | 先建事实边界，证据不够就降级表达或继续追问 |
| 一次抛出整套 STAR 问题 | 每次只问一个问题，并允许选择、跳过或只补一句 |
| 使用固定题库从头问到尾 | 根据简历、JD 和现场回答动态选择下一问 |
| 面试结束后给泛泛优缺点 | 判断回到原话，区分事实、推测、冲突和证据不足 |
| 给出标准答案后就结束 | 先让你作答，再针对缺口教学，最后换一种问法复测 |
| 把通用案例改写成候选人经历 | 案例只帮助理解和回忆，不自动进入简历或面试事实 |

## 它具体怎样工作？

四个 Skill 的任务不同，但底层都沿着同一条证据链工作：

```mermaid
graph LR
    classDef input fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef process fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#000;
    classDef output fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

    Material["简历 / JD / 面试记录"]:::input --> Fact["①：分清事实与待确认"]:::process
    Fact --> Target["②：找到岗位重点或回答缺口"]:::process
    Target --> Action["③：一次只改、问或练一个重点"]:::process
    Action --> Result["④：输出可解释的改写或诊断"]:::output
    Result --> Retest["⑤：需要时重答与复测"]:::output
    Retest -.->|"新证据"| Fact
```

这里的核心不是固定话术，而是闭环：先识别证据，再做判断；判断之后还要通过重答或复测确认是否真的改善。

## 这套 Skills 能帮你完成什么？

四个入口各做一件事：

| 你的任务 | 使用的 Skill | 你会得到 |
| --- | --- | --- |
| 整理或改写简历与配套材料 | `chengzicv-resume` | 一版能投的简历；经历证据不够时，再一题题补齐 |
| 针对项目、岗位知识或业务 Case 连续深挖 | `chengzicv-interview-practice` | 连续追问；问清后再反馈、讲解和复测 |
| 完成一场五题左右的企业初筛模拟 | `chengzicv-interview-mock` | 一场短模拟、企业视角复盘和针对性复练 |
| 复盘已经发生的真实面试 | `chengzicv-interview-review` | 逐题还原、表现诊断和下一次可以怎么答 |

## 我现在该选哪个入口？

这张图只解决一个问题：你现在该从哪个 Skill 开始。

```mermaid
graph LR
    classDef material fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff,stroke:#757575,stroke-width:2px,color:#000;
    classDef skill fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;

    Start["你手里有什么？"]:::material -->|"简历 / JD / 项目材料"| Goal{"现在最想解决什么？"}:::decision
    Goal -->|"先把材料改到能投"| Resume["简历优化"]:::skill
    Goal -->|"围绕项目或岗位能力深挖"| Practice["专项面试"]:::skill
    Goal -->|"模拟 HR / 综合初筛"| Mock["初筛模拟"]:::skill
    Start -->|"面试录音 / 逐字稿"| Review["真实面试复盘"]:::skill
```

- 简历优化：`$chengzicv-resume`
- 专项面试：`$chengzicv-interview-practice`
- 初筛模拟：`$chengzicv-interview-mock`
- 真实面试复盘：`$chengzicv-interview-review`

不用按固定顺序走。眼下需要什么，就从哪个入口开始。

## 怎么安装？

需要 Node.js 18 或更高版本。最简单的方式是用 [`skills` CLI](https://www.skills.sh/docs/cli) 一次安装四个 Skill：

```bash
npx -y skills add chengzicv/chengzicv-career-skills -g --all
```

只安装到一个客户端时，可以指定目标：

```bash
# Codex
npx -y skills add chengzicv/chengzicv-career-skills --skill '*' -g -a codex

# Claude Code
npx -y skills add chengzicv/chengzicv-career-skills --skill '*' -g -a claude-code

# WorkBuddy / CodeBuddy
npx -y skills add chengzicv/chengzicv-career-skills --skill '*' -g -a codebuddy
```

安装完成后重启对应客户端，再用 `$chengzicv-...` 调用。如果客户端能自动识别 Skill，也可以直接说“用 ChengziCV 帮我改简历”或“根据这份简历开始专项面试”。

## 安装后怎么开始？

不需要背复杂指令，交材料并说清当前目标即可：

```text
用 $chengzicv-resume 看这份简历和 JD。先给我一版能投的，再告诉我哪段经历最值得补证据。

用 $chengzicv-interview-practice 根据我的简历直接开始专项面试。先考后教，一次只问一个问题。

用 $chengzicv-interview-mock 根据我的简历开始一场企业初筛模拟。

用 $chengzicv-interview-review 复盘这份面试逐字稿。先告诉我表现，再把问题和回答逐题整理出来。
```

## 推荐什么客户端和模型？

**默认首选 Codex + GPT‑5.6 Sol High，或 Claude Code + Claude Sonnet 4.6。** 这类任务需要稳定读取多份材料、遵循长工作流、持续调用 Skill 引用文件，并在多轮对话中保持证据边界，客户端的 Agent 能力和模型本身同样重要。

以下是截至 **2026-08-07** 的建议；模型更新很快，请优先选择同系列中当前可用的更新型号。

| 推荐级别 | 客户端与模型 | 建议设置 | 适合什么情况 |
| --- | --- | --- | --- |
| 首选 | Codex + [GPT‑5.6 Sol](https://help.openai.com/en/articles/20001354-gpt-56-in-chatgpt/) | `High` | 多份简历材料、长面试记录、专项深挖和完整交付；质量与速度比较均衡 |
| 首选 | Claude Code + [Claude Sonnet 4.6](https://www.anthropic.com/news/claude-sonnet-4-6) 或当前更强型号 | 开启思考 | 长上下文、连续追问和自然中文表达；Sonnet 4.6 是推荐起点 |
| 高质量 | Claude Code + [Claude Opus 4.7](https://www.anthropic.com/claude/opus) | 开启思考 | 材料特别复杂、要求更高的判断和长程执行；通常更慢、成本更高 |
| 平衡型 | Codex + [GPT‑5.6 Terra](https://openai.com/index/gpt-5-6/) | `High` | 希望保留 Codex 的文件与工具能力，同时降低等待时间或成本 |
| 性价比 | WorkBuddy + [DeepSeek V4 Flash](https://api-docs.deepseek.com/news/news260424/) | Thinking，`High` | 文字版简历、常规面试练习和日常迭代；速度快、成本低 |
| 性价比增强 | WorkBuddy + DeepSeek V4 Pro | Thinking，复杂任务用 `Max` | Flash 容易漏掉长材料细节，或需要更稳的推理时 |

[WorkBuddy 支持安装 Skills](https://www.workbuddy.ai/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market) 和[配置自定义模型](https://www.workbuddy.ai/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Model)。DeepSeek V4 Flash 和 V4 Pro 官方均支持工具调用与长上下文；但 [DeepSeek 官方 WorkBuddy 接入示例](https://api-docs.deepseek.com/quick_start/agent_integrations/workbuddy/)将它们标记为不支持图片输入，因此处理截图、作品集、复杂 PDF 或视频时，优先使用具备多模态和文件工具的客户端，或者先把材料转成可靠文本。

### 怎么选最省心？

- 不想折腾：选 **Codex + GPT‑5.6 Sol High**。
- 已经在用 Claude Code：选 **Sonnet 4.6**；非常复杂的材料再换 Opus。
- 在意成本：选 **WorkBuddy + DeepSeek V4 Flash Thinking**；出现漏读、浅尝辄止或不按流程时换 V4 Pro。
- 简历只是小改：Terra 或 V4 Flash 通常够用。
- 要做专项深挖、长录音复盘或多文件作品集：优先 Sol High、Sonnet 4.6 或更强模型。
- 不要为了追求速度关闭思考模式；这套 Skills 的价值主要来自证据核验和多步判断。

## 哪些使用方式不推荐？

**不推荐把普通聊天窗口当成完整的 Agent Skill 运行环境。** 例如只把 `SKILL.md` 粘贴到元宝普通聊天模式，再期待它自动读取同目录的引用、脚本和规则，通常无法保证完整执行。

这不是说元宝或其他通用聊天产品不能回答求职问题，而是它们的普通聊天入口未必同时具备以下条件：

- 能安装并识别整个 Skill 目录，而不只是读取一段提示词；
- 能按需读取 `references/`、`schemas/` 和其他配套文件；
- 能稳定处理本地简历、JD、逐字稿、截图和多轮状态；
- 能调用脚本、文件工具或网页搜索核验结果；
- 能在长对话中持续遵守“一次一问、证据优先、先考后教”等行为约束。

判断一个客户端是否适合，不看它宣传的模型名字，而看它能否完整加载 Skill、访问所需材料、调用工具并保持多轮工作流。只想临时问一个问题时，普通聊天当然可以；要跑完整简历优化或面试训练，优先使用 Codex、Claude Code 或 WorkBuddy 这类 Agent 客户端。

## 它会不会替我编经历？

不会。经历、数字、结果和个人贡献，只能来自你提供的材料或现场回答。

- 简历里的待确认信息和教学案例，不会被当成真实经历。
- 面试诊断尽量回到你的原话，不凭表达印象下结论。
- 没问到的能力不会被直接判低分。
- 通用参考答案不会被倒写成你的项目做法。

## 隐私数据会保存到哪里？

这些 Skill 不包含真实候选人数据，也不会自行把材料保存到本地。普通聊天只使用当前对话里能看到的内容；如果接入其他产品，数据怎么保存由对应产品决定。

求职材料通常包含姓名、电话、邮箱、教育经历和工作记录。使用前请确认所用平台的数据政策，不要把未脱敏的候选人材料提交到不受信任的服务，也不要把真实面试记录直接提交到公开 issue、公开日志或示例文件中。

## 使用边界

- 这是候选人训练与材料整理工具，不代表任何企业的内部录用标准。
- 不输出录用概率，也不承诺使用后一定通过面试。
- 不依据性别、年龄、籍贯、婚育、健康、民族、宗教或政治倾向作负面判断。
- 初筛模拟不替代算法、编码、系统设计或岗位专家 Case。
- 涉及时效性规则、法律、财税、平台政策或其他高风险专业判断时，应先核验可靠来源。
- AI 生成内容仍需人工核对，尤其是数字、个人贡献、技术实现和可外发材料。

## 项目结构

```text
.
├── chengzicv-resume/
├── chengzicv-interview-practice/
├── chengzicv-interview-mock/
├── chengzicv-interview-review/
└── README.md
```

每个目录中的 `SKILL.md` 定义触发条件和核心工作流；`references/` 保存按需加载的方法与模板；`scripts/`、`schemas/` 和 `runtime/` 只在对应 Skill 需要确定性校验或产品集成时使用。

## 许可证

本项目采用 [MIT License](LICENSE)。
