---
name: chengzicv-update
description: 更新或重新同步官方 ChengziCV 求职 Skills。仅在用户明确提出“更新 ChengziCV Skills”“升级橙子简历 Skills”“重新安装最新版”等请求时使用；如果用户只是询问版本、更新内容或是否需要更新，只回答问题，不执行安装。
---

# ChengziCV Update

把官方 ChengziCV 求职 Skills 重新同步到用户当前使用的 Agent，不改动其他来源的 Skills，也不处理用户的简历、档案或面试材料。

## 更新流程

1. 确认用户是在明确要求实际更新，而不是只询问版本或更新说明。
2. 如果当前 Agent 能执行终端命令，直接运行：

   ```bash
   npx -y skills add chengzicv/chengzicv-career-skills -g --all
   ```

   用户已经明确要求更新时，不再追加一次文字确认；宿主环境自己的命令执行授权仍然有效。
3. 等待命令结束并检查退出状态。成功时说明官方 Skills 已重新同步，并提醒用户：如果当前客户端没有立即识别新版本，请重启客户端或新建对话。
4. 失败时只报告关键错误和一个可执行的下一步，不虚构成功状态。

## 无终端环境

如果当前 Agent 不能执行终端命令，不声称已经自动更新。让用户下载最新版安装包并重新导入：

<https://github.com/chengzicv/chengzicv-career-skills/releases/latest/download/chengzicv-career-skills.zip>

## 边界

- 只同步 `chengzicv/chengzicv-career-skills`，不运行会批量更新其他来源 Skill 的命令。
- 不创建后台任务、登录项、定时器、钩子或常驻进程；更新只在用户当次明确请求时发生。
- 不删除或修改用户的求职材料、聊天记录和其他 Skills。
- 不使用 `npx skills update` 代替上述安装命令，避免把不在本次范围内的 Skills 一并更新。
- 用户只询问当前版本、更新日志或是否存在新版本时，先核验信息再回答，不执行更新。
