# Word Update Skill

_自动化更新 GitHub 和飞书文档_

> ⚠️ **重要**：本 Skill 是**流程文件**，使用 Python 脚本确保上传成功。

## 概述

本 Skill 用于自动化更新 GitHub 仓库和飞书文档，确保每次更新都能完整同步。

## 触发条件

当用户说以下内容时激活：
- "上传更新"
- "更新文件"
- "同步到"
- "word_update"
- 需要将本地修改同步到 GitHub 或飞书时

---

## 📋 完整流程

### 步骤 1：确认需要更新的内容

询问用户需要更新的内容：
- 更新了哪些文件？
- 更新描述（用于 commit message）？
- 需要更新到哪些平台？（GitHub / 飞书 / 全部）

### 步骤 2：执行更新

调用 Python 脚本执行更新：

```bash
python3 ~/.openclaw/skills/word_update/word_update.py --desc "更新描述" --target github,feishu
```

**参数说明**：
- `--desc`：更新描述（必填）
- `--target`：更新目标，可选值：
  - `github`：仅 GitHub
  - `feishu`：仅飞书
  - `all`：全部（默认）

### 步骤 3：返回结果

根据脚本执行结果返回：
- 成功：显示更新详情
- 失败：显示错误信息并提供解决方案

---

## 🔧 Python 脚本功能

`word_update.py` 脚本负责：

1. **GitHub 更新**
   - 进入 skills 目录
   - `git add -A`
   - `git commit -m "<描述>"`
   - `git push origin main`
   - 错误处理和重试机制

2. **飞书更新**
   - 更新版本记录文档
   - 自动刷新主管理表

---

## ⚠️ 注意事项

1. **更新描述必填**：必须提供有意义的描述
2. **目标默认全部**：如果不指定 target，默认更新全部
3. **失败重试**：脚本会自动重试最多 3 次

---

## 📝 使用示例

```
用户：上传一下刚才的修改
Agent：请提供更新描述：
       例如：更新 model-switcher Skill

用户：添加了新的 word_update Skill

Agent：执行更新...
       ✅ GitHub 已更新
       ✅ 飞书已更新
       更新完成！
```

---

_Last updated: 2026-02-16 21:20_
