# Memory Search CLI Skill

_通过 CLI 命令搜索本地记忆文件_

## 概述

本 Skill 用于在**记忆搜索场景**下，通过调用本地 qmd 命令行工具进行搜索。当需要查找之前对话、记录、偏好等信息时使用。

**重要**：本 Skill 仅限于**记忆搜索**场景使用，不可用于其他用途。

## 触发条件

当用户说以下内容时激活：
- "搜索记忆"
- "查找之前的对话"
- "搜索之前的记录"
- "查找我的笔记"
- "搜索 MEMORY.md"
- "查找以前的事情"
- "我之前说过什么"
- "搜索 memory 文件"

## 限制

### ⚠️ 安全约束

1. **仅限记忆搜索**：本 Skill 只能用于搜索 `memory/` 目录下的文件和会话记录
2. **只读操作**：仅执行搜索命令，不执行任何写入/修改操作
3. **无副作用**：搜索操作不会修改任何文件或系统状态
4. **禁止场景**：
   - ❌ 文件写入/删除
   - ❌ 系统命令执行
   - ❌ 网络请求（搜索除外）
   - ❌ 任何可能影响环境的操作

## 操作流程

### 步骤 1：解析用户需求
用户触发记忆搜索时，提取搜索关键词。

### 步骤 2：执行搜索
使用 qmd 命令行工具执行搜索：

```bash
XDG_CONFIG_HOME=~/.openclaw/agents/main/qmd/xdg-config \
XDG_CACHE_HOME=~/.openclaw/agents/main/qmd/xdg-cache \
qmd search "关键词" -c memory-root --json
```

或搜索会话记录：
```bash
XDG_CONFIG_HOME=~/.openclaw/agents/main/qmd/xdg-config \
XDG_CACHE_HOME=~/.openclaw/agents/main/qmd/xdg-cache \
qmd search "关键词" -c sessions --json
```

### 步骤 3：格式化结果
将搜索结果格式化后展示给用户，包含：
- 匹配的文档路径
- 相关内容片段
- 匹配分数

### 步骤 4：展示结果
以清晰的格式向用户展示搜索结果。

## 注意事项

1. **搜索范围**：
   - `memory-root`：搜索 `MEMORY.md` 长期记忆
   - `sessions`：搜索会话记录
   - 可同时搜索两个 collection

2. **搜索模式**：使用 BM25 纯文本搜索，无需 API Key

3. **结果限制**：默认返回前 8 条结果

4. **无结果处理**：如果搜索无结果，告知用户并建议尝试其他关键词
