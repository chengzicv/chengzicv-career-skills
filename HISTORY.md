# ChengziCV 历史版本恢复

2026-10-13 删除 19 个未启用的历史版本目录，历史内容保存在清理前的 Git 提交中。

清理前提交：`55629af6fd978803083d41b81eacadcdab7db463`，已推送至统一 Skills 仓库的 `origin/master`。

当前使用 `chengzicv-resume-latest` 和 `chengzicv-case-factory-latest`。版本登记只列现存 latest，保留下一版编号 v13、v8，避免重复使用历史编号。

## 查看或恢复

在统一 Skills 仓库根目录执行。只查看文件：

```bash
git show 55629af6fd978803083d41b81eacadcdab7db463:chengzicv-resume-v12/references/dual-lens-header.md
```

恢复某个旧目录到工作区（不会改动 latest，也不会自动启用）：

```bash
git restore --source=55629af6fd978803083d41b81eacadcdab7db463 --worktree -- chengzicv-resume-v12
```

早期版本存在跨版本文件链接；恢复这类目录时，也要从同一提交恢复链接指向的版本。

需要回滚当前行为时，先保存当前 latest，再将恢复的旧版内容迁入 latest 并调整 name、默认调用名和正文引用；不要直接启用历史入口。

旧测试报告保留当时的目录和版本名，引用的文件可通过上述提交查看。

## 已删除目录

- `chengzicv-case-factory`
- `chengzicv-case-factory-v2`
- `chengzicv-case-factory-v3`
- `chengzicv-case-factory-v4`
- `chengzicv-case-factory-v5`
- `chengzicv-case-factory-v6`
- `chengzicv-case-factory-v7`
- `chengzicv-resume`
- `chengzicv-resume-v2`
- `chengzicv-resume-v3`
- `chengzicv-resume-v4`
- `chengzicv-resume-v5`
- `chengzicv-resume-v6`
- `chengzicv-resume-v7`
- `chengzicv-resume-v8`
- `chengzicv-resume-v9`
- `chengzicv-resume-v10`
- `chengzicv-resume-v11`
- `chengzicv-resume-v12`
