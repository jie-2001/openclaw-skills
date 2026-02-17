---
name: memory-optimizer
description: 记忆优化器 - 自动压缩过长的对话记忆，创建优秀记忆文件，减少加载时间
metadata: { "openclaw": { "emoji": "🧠", "version": "1.0.1", "requires": { "bins": ["jq", "rg"] } } }
---

> **测试版本 v1.0.2** - 用于测试 word_update Skill

# memory-optimizer

记忆优化器 - 自动将过长的对话记忆压缩成"优秀记忆"，优化读取性能。

## 概述

当对话历史过长时，每次加载全部记忆会消耗大量时间和 token。本 skill 实现自动压缩机制：

1. **检测阈值** - 检查对话是否超过设定阈值
2. **创建优秀记忆** - 语义压缩对话内容，提取关键信息
3. **增量更新** - 后续对话只追加，不重复压缩

---

## 触发条件

**自动触发**（在以下情况激活）：

- 用户说"优化记忆"、"压缩记忆"、"整理记忆"
- 对话累积超过阈值（默认 50KB 或 100 条消息）
- 新会话开始时检测到历史对话过长

**手动触发**：

- 用户明确要求执行记忆优化

---

## 存储位置

| 类型 | 路径 |
|------|------|
| 对话记录 | `~/.openclaw/agents/main/sessions/*.jsonl` |
| 优秀记忆 | `~/.openclaw/workspace/memory/optimized/` |
| 元信息 | `~/.openclaw/workspace/memory/*.md` |

---

## 使用方法

### 1. 手动优化记忆

当用户说"优化记忆"时执行：

```bash
# 检查当前对话大小
SIZE=$(du -k ~/.openclaw/agents/main/sessions/*.jsonl | awk '{sum+=$1} END {print sum}')
echo "当前对话总大小: ${SIZE}KB"

# 检查是否需要优化
if [ "$SIZE" -gt 50000 ]; then
  echo "需要优化"
else
  echo "不需要优化"
fi
```

### 2. 创建优秀记忆

```bash
# 创建优化目录
mkdir -p ~/.openclaw/workspace/memory/optimized

# 生成优秀记忆文件
OPTIMIZED_FILE="~/.openclaw/workspace/memory/optimized/optimized-$(date +%Y-%m-%d).md"

# 写入压缩后的记忆
cat > "$OPTIMIZED_FILE" << 'EOF'
# 优秀记忆 - {日期}

## 组成对话
- session-id-1: {日期} - {主题摘要}
- session-id-2: {日期} - {主题摘要}

## 关键信息
- {提取的关键决策}
- {重要的偏好设置}
- {待办事项}

## 重要上下文
{保留的重要上下文和引用来源}

---
创建时间: {timestamp}
更新时间: {timestamp}
EOF
```

### 3. 读取优化流程

当需要读取记忆时：

```bash
# 检查是否有优秀记忆
OPTIMIZED_DIR="~/.openclaw/workspace/memory/optimized"
if [ -d "$OPTIMIZED_DIR" ] && [ "$(ls -A $OPTIMIZED_DIR)" ]; then
  # 读取最新的优秀记忆
  LATEST_OPT=$(ls -t $OPTIMIZED_DIR/optimized-*.md | head -1)
  echo "读取优秀记忆: $LATEST_OPT"
  cat "$LATEST_OPT"
  
  # 读取未收录的后续对话
  echo "--- 后续对话 ---"
  # TODO: 读取未收录的对话
else
  # 无优秀记忆，读取全部
  echo "无优秀记忆，读取全部对话"
fi
```

---

## 压缩算法

### 语义压缩步骤

1. **提取用户消息** - 过滤出 user 角色的消息
2. **提取关键决策** - 识别包含决策、结论、约定的对话
3. **提取偏好设置** - 识别用户偏好、规则、配置
4. **生成摘要** - 将每段对话压缩为一行关键信息

### 示例

**原始对话**（100+ 条）：
```
用户: 记住我叫张三
用户: 我喜欢深色模式
用户: 以后叫我 小明 就行
AI: 好的，已记录
用户: 设置提醒每天早上9点
...
```

**压缩后**：
```
## 关键信息
- 用户名: 张小明（小明）
- 界面偏好: 深色模式
- 日常提醒: 每天早上9点
```

---

## 增量更新机制

### 检测未收录对话

```bash
# 获取优秀记忆中的最新对话时间
LAST_OPTIMIZED="2026-02-15"

# 读取该时间之后的新对话
for f in ~/.openclaw/agents/main/sessions/*.jsonl; do
  SESSION_DATE=$(basename "$f" .jsonl | cut -d'-' -f1-3)
  if [[ "$SESSION_DATE" > "$LAST_OPTIMIZED" ]]; then
    echo "新对话: $f"
  fi
done
```

### 重新优化

当累积新对话超过阈值时：
1. 读取现有优秀记忆
2. 合并新对话的关键信息
3. 生成新的优秀记忆文件
4. 更新组成列表

---

## 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 阈值大小 | 50KB | 超过此大小触发优化 |
| 阈值消息数 | 100条 | 超过此数量触发优化 |
| 保留天数 | 30天 | 优秀记忆保留时间 |
| 压缩级别 | 中等 | 可选: 轻/中/重 |

---

## 注意事项

- ✅ 优秀记忆是**增量**的，不是每次都重新压缩全部历史
- ✅ 优先保证信息不丢失，再考虑压缩效率
- ✅ 定期检查是否有未收录的对话
- ❌ 不要删除原始对话文件，只创建压缩版本

---

## 快速命令

```bash
# 检查记忆大小
du -sh ~/.openclaw/agents/main/sessions/

# 查看优秀记忆列表
ls -la ~/.openclaw/workspace/memory/optimized/

# 查看最新优秀记忆
cat ~/.openclaw/workspace/memory/optimized/optimized-*.md | head -50

# 手动触发优化
# 运行本 skill 的压缩流程
```
