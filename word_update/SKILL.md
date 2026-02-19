# Word Update Skill

_自动化更新 GitHub 和飞书文档_

> ⚠️ **重要**：本 Skill 是**流程文件**，使用 Python 脚本 + OpenClaw 工具确保上传成功。

## 概述

本 Skill 用于自动化更新 GitHub 仓库和飞书文档，支持**自动检测本地修改**，确保每次更新都能完整同步。

## 触发条件

### 自动触发（新增）
当检测到本地 skills 有修改时自动提示：
- GitHub 仓库有未提交的修改（通过 git status 检测）
- 本地 skills 目录有新增/删除/修改的文件

### 手动触发
当用户说以下内容时激活：
- "上传更新"
- "更新文件"
- "同步到"
- "word_update"
- 需要将本地修改同步到 GitHub 或飞书时

---

## 📋 完整流程

### 步骤 0：自动检测（新增）

**每次新会话开始时自动执行**：

```bash
# 检查 GitHub 仓库状态
cd ~/.openclaw/skills && git status --porcelain

# 检查是否有未提交的修改
# 如果有，提示用户是否需要更新
```

### 步骤 1：确认需要更新的内容

1. **自动列出修改内容**：
   - 显示新增/修改/删除的文件列表
   - 对于 SKILL.md 文件，提取 Skill 名称和版本变化

2. 询问用户：
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

### 步骤 4：返回结果

汇总结果并返回给用户：
- GitHub 更新结果
- 飞书更新结果
- 失败信息（如有）

---

## 🔧 自动检测逻辑（新增）

### 检测内容

| 类型 | 检测方式 | 处理方式 |
|------|---------|---------|
| 新增文件 | `git status --porcelain` | 提示用户确认 |
| 修改文件 | `git diff --name-only` | 提取变更内容 |
| 删除文件 | `git status --porcelain` | 标记为已删除，更新飞书 |

### 检测脚本

```bash
#!/bin/bash
# auto_detect_changes.sh

cd ~/.openclaw/skills

# 获取未提交的修改
status=$(git status --porcelain)

if [ -n "$status" ]; then
    echo "⚠️ 检测到本地有修改："
    echo "$status"
    echo ""
    echo "是否需要上传更新？(y/n)"
else
    echo "✅ 本地已是最新，无需更新"
fi
```

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
4. **删除处理**：删除的文件在飞书中标记为"已删除"，保留删除记录

---

## 📝 使用示例

### 自动检测示例

```
Agent（自动检测）：
⚠️ 检测到本地有修改：
M  ai-news-digest/SKILL.md
M  browser-use/SKILL.md
D  memory-optimizer/SKILL.md
D  memory-optimizer/optimizer.sh
A  memory-engine/SKILL.md

是否需要上传更新？(y/n)
```

### 手动触发示例

```
用户：上传一下刚才的修改

Agent：自动检测到以下修改：
- ai-news-digest: 增强论文检索功能
- browser-use: 升级CLI命令支持
- memory-optimizer: 已删除（整合到memory-engine）
- memory-engine: 新安装

更新描述：升级skills - memory-engine安装, browser-use升级

开始更新...
1. GitHub 更新... ✅
2. 飞书更新... ✅

🎉 全部更新完成！
```

---

## 📜 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.1.0 | 2026-02-19 | 添加自动检测本地修改功能 |
| v1.0.4 | 2026-02-17 | 添加版本管理、自动递增版本号 |
| v1.0.3 | 2026-02-16 | 优化检验功能 |
| v1.0.0 | 2026-02-15 | 初始版本 |

---

_Last updated: 2026-02-19 14:15_
