---
name: chengzicv-update
description: 更新或重新同步官方 ChengziCV 求职 Skills。仅在用户明确提出“更新 ChengziCV Skills”“升级橙子简历 Skills”“重新安装最新版”等请求时使用；如果用户只是询问版本、更新内容或是否需要更新，只回答问题，不执行安装。
---


<!-- jc-skill-installer:route:start -->
## 本机统一 Skill 管理规则

本 Skill 已接入 JC 统一仓库。执行安装、更新、停用或迁移前，先读取同一仓库的 `jc-skill-installer/SKILL.md`，由该管理器负责最终存储、活动清单和所有客户端同步。

在这台机器上，不执行下文的全局 `npx skills add ... -g --all`，不创建 `.agents/skills` 或 Grok 薄适配层，也不按旧脚本清理客户端专属入口。下文这些独立安装步骤仅适用于未接入 JC 管理器的环境。

新增：把候选文件放到统一仓库，检查名称及已有改动，然后执行 `python3 /Users/codemao/.cc-switch/skills/jc-skill-installer/scripts/manage.py activate <仓库相对路径>`。更新：先获取上游到临时目录，比较、保存本地修改与旧内容，仅替换对应的统一源文件，遵循已注册的版本归档规则，最后执行 `python3 /Users/codemao/.cc-switch/skills/jc-skill-installer/scripts/manage.py update <仓库相对路径>`；更新整个套件后可执行 `python3 /Users/codemao/.cc-switch/skills/jc-skill-installer/scripts/manage.py reconcile`。停用：执行 `python3 /Users/codemao/.cc-switch/skills/jc-skill-installer/scripts/manage.py deactivate <skill-name>`。

管理器检查成功后才能报告完成；失败时保留源文件与原有用户材料，处理冲突后重跑。
<!-- jc-skill-installer:route:end -->

# ChengziCV Update

把官方 ChengziCV 求职 Skills 重新同步到用户当前使用的 Agent，不改动其他来源的 Skills，也不处理用户的简历、档案或面试材料。

## 更新流程

1. 确认用户是在明确要求实际更新，而不是只询问版本或更新说明。
2. 保护用户工作区：先读取用户主目录下的 `.chengzicv/workspace.json`，外部工作区和位置配置不参与 Skill 更新，不删除、不重建、不迁移。兼容旧版：如果 `chengzicv` Skill 目录下存在 `workspace/` 或 `chengzicv-workspace/` 文件夹（求职档案、上传材料副本、产出文件），先把它完整复制到 Skill 目录之外的临时位置；更新命令结束并确认成功后，再把它原样复制回原来的 `chengzicv/workspace/` 或 `chengzicv/chengzicv-workspace/`，随后删除临时副本。用户的档案和材料任何情况下不得因更新丢失。
3. 如果当前 Agent 能执行终端命令，直接运行：

   ```bash
   npx -y skills add chengzicv/chengzicv-career-skills -g --all
   ```

   用户已经明确要求更新时，不再追加一次文字确认；宿主环境自己的命令执行授权仍然有效。
4. 等待命令结束并检查退出状态。成功时说明官方 Skills 已重新同步，并提醒用户：如果当前客户端没有立即识别新版本，请重启客户端或新建对话。
5. 失败时只报告关键错误和一个可执行的下一步，不虚构成功状态。

## 无终端环境

如果当前 Agent 不能执行终端命令，不声称已经自动更新。让用户下载最新版安装包并重新导入：

<https://github.com/chengzicv/chengzicv-career-skills/releases/latest/download/chengzicv-career-skills.zip>

## 边界

- 只同步 `chengzicv/chengzicv-career-skills`，不运行会批量更新其他来源 Skill 的命令。
- 不创建后台任务、登录项、定时器、钩子或常驻进程；更新只在用户当次明确请求时发生。
- 不删除或修改用户的求职材料、聊天记录和其他 Skills。
- 不使用 `npx skills update` 代替上述安装命令，避免把不在本次范围内的 Skills 一并更新。
- 用户只询问当前版本、更新日志或是否存在新版本时，先核验信息再回答，不执行更新。
