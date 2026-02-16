# Word Update Skill

_自动化更新 GitHub 和飞书文档_

> ⚠️ **重要**：本 Skill 是**流程文件**，使用 Python 脚本 + OpenClaw 工具确保上传成功。

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

询问用户：
- 更新了哪些 Skill？
- 更新描述（用于 commit message）？
- 需要更新到哪些平台？（GitHub / 飞书 / 全部）

### 步骤 2：GitHub 更新（Python 脚本）

调用 Python 脚本执行 GitHub 更新：

```bash
python3 ~/.openclaw/skills/word_update/word_update.py --desc "<更新描述>" --target github
```

### 步骤 3：飞书更新（OpenClaw 工具）

**飞书更新必须通过 OpenClaw 会话中的 feishu_doc 工具完成**：

1. **更新版本记录**：使用 `feishu_doc` 工具的 `append` 或 `write` action
2. **更新主管理表**：使用 `feishu_doc` 工具更新管理表

示例：
```
# 更新版本记录（追加新版本）
feishu_doc --action append --doc_token <文档ID> --content "## v1.0.1 (2026-02-16)\n\n更新内容..."

# 更新主管理表
feishu_doc --action write --doc_token YMr1dySwToBwSpxTJrpcNZODnCc --content "..."
```

### 步骤 4：返回结果

汇总结果并返回给用户：
- GitHub 更新结果
- 飞书更新结果
- 失败信息（如有）

---

## 🔧 各平台更新方式

| 平台 | 更新方式 | 工具 |
|------|---------|------|
| **GitHub** | Python 脚本 | `word_update.py` |
| **飞书** | OpenClaw 工具 | `feishu_doc` |

---

## ⚠️ 重要说明

1. **飞书更新必须在 OpenClaw 会话中**：Python 脚本无法调用飞书 API，需要 Agent 使用 feishu_doc 工具
2. **先 GitHub 后飞书**：先执行脚本上传 GitHub，再在会话中更新飞书
3. **更新描述必填**：必须提供有意义的描述

---

## 📝 使用示例

```
用户：上传一下刚才的修改

Agent：请提供更新描述：
       例如：更新 model-switcher Skill

用户：修复了 Bug

Agent：
1. 执行 GitHub 更新...
   ✅ GitHub 已更新
   
2. 更新飞书版本记录...
   ✅ 飞书已更新
   
🎉 全部更新完成！
```

---

_Last updated: 2026-02-16 21:30_
