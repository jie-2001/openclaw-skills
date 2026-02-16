# Model Switcher Skill

_在对话中自由切换模型_

> ⚠️ **重要**：本 Skill 是**流程文件**，不是简单的提示词。请严格按照以下流程执行。

## 触发条件

当用户说以下内容时激活：
- "切换模型"
- "换模型"
- "换一个模型"
- "切换到 XXX 模型"
- "用 XXX 模型"

---

## 📋 完整流程（必须严格按顺序执行）

### 步骤 1：用户触发 → 展示模型列表

当用户说"切换模型"或类似话语时，**不要立即切换**，而是：

1. 展示可用模型列表（必须步骤）

```
📋 可用模型列表：

【本地模型 (Ollama)】
1. ollama/qwen3:30b - Qwen3-30B (本地)
2. ollama/qwen3:8b - Qwen3-8B (本地)
3. ollama/qwen3-coder:30b - Qwen3-Coder-30B (本地)

【联网模型】
4. minimax-portal/MiniMax-M2.5 - MiniMax M2.5 (200K context)
5. minimax-portal/MiniMax-M2.1 - MiniMax M2.1
6. qwen-portal/coder-model - Qwen Coder
7. qwen-portal/vision-model - Qwen Vision

请回复模型编号或名称进行切换（如：1 或 ollama/qwen3:30b）
```

### 步骤 2：等待用户选择

**必须等待用户明确选择**后才能执行下一步。不能替用户做决定。

### 步骤 3：验证输入

获得用户回复后，验证输入是否有效：
- 用户可能回复编号（如 "1"）或完整 ID（如 "ollama/qwen3:30b"）
- 如果是编号，转换为对应的模型 ID
- 如果无法识别，**重新询问**，不要尝试猜测

### 步骤 4：执行切换

使用 `session_status` 工具进行模型切换：

```json
{
  "model": "ollama/qwen3:30b"
}
```

### 步骤 5：调用 Python 脚本调整 Hook

**关键步骤**：调用 Python 脚本执行实际的 Hook 调整。

脚本路径：`~/.openclaw/skills/model-switcher/model_switcher.py`

```bash
python3 ~/.openclaw/skills/model-switcher/model_switcher.py <目标模型ID>
```

示例：
```bash
# 切换到本地模型
python3 ~/.openclaw/skills/model-switcher/model_switcher.py ollama/qwen3:30b

# 切换到云端模型
python3 ~/.openclaw/skills/model-switcher/model_switcher.py minimax-portal/MiniMax-M2.5
```

### 步骤 6：确认切换成功

根据切换结果回复用户：

**本地模型切换成功**：
```
✅ 模型已切换为【Qwen3-30B (本地)】
- 此切换仅在当前会话中生效
- session-memory hook 已自动关闭
- 如需恢复记忆功能，请切换回云端模型
```

**云端模型切换成功**：
```
✅ 模型已切换为【MiniMax M2.5 (云端)】
- 此切换仅在当前会话中生效
- session-memory hook 已自动开启
```

---

## 🔧 Python 脚本功能

`model_switcher.py` 脚本负责：

1. **接收目标模型 ID**
2. **判断模型类型**：
   - 本地模型：以 `ollama/` 开头
   - 云端模型：其他所有模型
3. **读取当前 Hook 状态**
4. **自动调整**：
   - 本地模型 → 关闭 Hook
   - 云端模型 → 开启 Hook

---

## ⚠️ 禁止事项

1. **不要**在用户未明确选择时就切换模型
2. **不要**跳过步骤 5（Python 脚本调用）
3. **不要**假设用户的输入一定是正确的，必须验证

---

## 📝 模型列表（备用）

| 编号 | 模型 ID | 类型 |
|------|---------|------|
| 1 | ollama/qwen3:30b | 本地 |
| 2 | ollama/qwen3:8b | 本地 |
| 3 | ollama/qwen3-coder:30b | 本地 |
| 4 | minimax-portal/MiniMax-M2.5 | 云端 |
| 5 | minimax-portal/MiniMax-M2.1 | 云端 |
| 6 | qwen-portal/coder-model | 云端 |
| 7 | qwen-portal/vision-model | 云端 |

---

_Last updated: 2026-02-16 21:00_
