# ChengziCV 发布与安装包边界

## 单一来源

ChengziCV 各 Skill 的真实源文件位于本机统一 Skills 仓库中，与 `chengzicv-career-skills/` 同级。公开 GitHub 仓库是发布镜像，不作为另一份长期手工维护的源文件。

当前公开包包含 11 个组件：

- 总入口：`chengzicv`；
- 求职执行：`chengzicv-profile`、`chengzicv-career`、`chengzicv-resume`、`chengzicv-job-greeting`、`chengzicv-interview-prep`、`chengzicv-interview-mock`、`chengzicv-interview-practice`、`chengzicv-interview-review`、`chengzicv-case-factory`；
- 更新入口：`chengzicv-update`。

`chengzicv-light-business-intake` 是内部 To B 工具，不进入 C 端公开仓库、GitHub Release 或 SkillHub 包。

## 用户运行文件

每个 Skill 只分发运行时会使用的内容：

- `SKILL.md` 与 `agents/openai.yaml`；
- 首次使用的 `onboarding/`；
- 按条件读取的 `references/`；
- 确定性校验所需的 `scripts/`、`schemas/`、`runtime/`、`scorecards/` 与 `prompts/`；
- 实际产物需要复制的 `assets/`。

总入口的 `references/journey-contract.md` 属于运行契约，随 `chengzicv` 分发。不要把 `.DS_Store`、缓存、真实候选人材料、临时输出、历史测试报告或本地密钥放进安装包。SkillHub 不接受无扩展名的 `LICENSE`，许可证通过根 `SKILL.md` 的 `license: MIT` 声明，完整文件保留在 GitHub 仓库。

## 两种发布包

运行 `python3 tools/build_release.py` 会从同一份源码生成两种确定性 ZIP：

1. `dist/skills/chengzicv-career-skills.zip`：GitHub Release 与 WorkBuddy 等手工安装场景使用。只保留一个外层 ZIP；解压后是 `chengzicv-career-skills/` 总目录和 11 个完整 Skill 文件夹，不允许再嵌套 ZIP。
2. `dist/skillhub/chengzicv-career-skills-<version>.zip`：SkillHub 使用。根目录是带平台元数据的 `SKILL.md`，其余公开成员位于 `skills/` 下。

运行 `python3 tools/verify_release.py` 检查版本、公开成员、内部工具隔离、ZIP 结构和危险文件。发布前必须同时通过构建与验证。

## 导出到公开 GitHub 仓库

先克隆公开仓库到干净目录，再从本机单一来源导出：

```bash
git clone git@github.com:chengzicv/chengzicv-career-skills.git <临时目录>
python3 <统一Skills仓库>/chengzicv-career-skills/tools/sync_public_repo.py <临时目录>
```

`sync_public_repo.py` 只同步公开清单、README、依赖与发版文件，不复制内部 To B Skill、真实候选人材料或统一 Skills 仓库中的其他内容。同步后先查看 `git diff`，再构建和提交。

## GitHub 发版

根目录 `VERSION` 使用 SemVer。Git tag 必须与它一致：

```bash
python3 tools/build_release.py
python3 tools/verify_release.py
git push origin main
git tag vX.Y.Z
git push origin vX.Y.Z
```

推送 `v*` 标签后，GitHub Actions 会重新校验版本、构建安装包，并自动创建 Release。不要提交 `dist/`。

## SkillHub 发版

GitHub Release 验证通过后，再发布同一提交构建出的 SkillHub ZIP：

```bash
skillhub publish dist/skillhub/chengzicv-career-skills-X.Y.Z.zip \
  --version X.Y.Z \
  --changelog "本次更新说明" \
  --dry-run

skillhub publish dist/skillhub/chengzicv-career-skills-X.Y.Z.zip \
  --version X.Y.Z \
  --changelog "本次更新说明"

skillhub verify '@user_1f99808e/chengzicv-career-skills@X.Y.Z' \
  --zip dist/skillhub/chengzicv-career-skills-X.Y.Z.zip
```

平台版本、根 `SKILL.md` 的 `version` 和 GitHub `VERSION` 必须一致，禁止再用 `--version` 覆盖出“平台版本已升级、包内版本未升级”的版本。

## 开发仓库保留内容

以下内容可以保留在开发仓库，但不放进单个用户 Skill：

- `evals/` 中的触发、回归和端到端评测；
- 依赖审计、发布清单和设计记录；
- 历史基准输出与测试报告；
- `dist/` 中的本地构建产物。

已经被真实失败证明、会改变 Agent 行为的规则，应写进 `SKILL.md` 或对应 Reference；测试这些规则的案例留在开发仓库。
