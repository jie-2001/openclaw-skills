# Model Switcher Skill

_在对话中自由切换模型_

## 触发条件

当用户说以下内容时激活：
- "切换模型"
- "换模型"
- "换一个模型"
- "切换到 XXX 模型"
- "用 XXX 模型"

## 模型分类

### 本地模型 (Ollama)
- `ollama/qwen3:30b` - Qwen3-30B (本地)
- `ollama/qwen3:8b` - Qwen3-8B (本地)
- `ollama/qwen3-coder:30b` - Qwen3-Coder-30B (本地)

### 云端模型
- `minimax-portal/MiniMax-M2.5` - MiniMax M2.5 (200K context)
- `minimax-portal/MiniMax-M2.1` - MiniMax M2.1
- `qwen-portal/coder-model` - Qwen Coder
- `qwen-portal/vision-model` - Qwen Vision
- `custom-integrate-api-nvidia-com/z-ai/glm4.7` - GLM-4.7
- `custom-integrate-api-nvidia-com/moonshotai/kimi-k2.5` - Kimi K2.5

## 操作流程（重要修正）

### 步骤 1：用户触发
用户说"切换模型"或类似话语。

### 步骤 2：展示列表（必须步骤）
**必须先展示可用模型列表**，不能直接切换。回复格式：

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

### 步骤 3：等待用户选择
**必须等待用户明确选择**后才能执行切换，不能替用户做决定。

### 步骤 4：执行切换
使用 `session_status` 工具的 `model` 参数进行切换：

```json
{
  "model": "ollama/qwen3:30b"
}
```

### 步骤 5：调整 Memory Hook（关键步骤）

切换模型后，**必须**根据模型类型自动调整 session-memory hook：

#### 判断模型类型
- **本地模型**：ID 以 `ollama/` 开头
- **云端模型**：其他所有模型

#### 执行调整

**切换到本地模型时**：
使用 `gateway` 工具的 `config.patch` 关闭 hook：

```json
{
  "action": "config.patch",
  "patch": {
    "hooks": {
      "internal": {
        "entries": {
          "session-memory": {
            "enabled": false
          }
        }
      }
    }
  },
  "note": "已为本地模型关闭 session-memory hook"
}
```

**切换到云端模型时**：
使用 `gateway` 工具的 `config.patch` 开启 hook：

```json
{
  "action": "config.patch",
  "patch": {
    "hooks": {
      "internal": {
        "entries": {
          "session-memory": {
            "enabled": true
          }
        }
      }
    }
  },
  "note": "已为云端模型开启 session-memory hook"
}
```

### 步骤 6：确认切换
告诉用户切换成功（本地模型）：
```
✅ 模型已切换为【Qwen3-30B (本地)】
- 此切换仅在当前会话中生效
- 关闭对话后将恢复为默认模型
- 您的配置和记忆不受影响
- session-memory hook 已关闭（本地模型）
```

或（云端模型）：
```
✅ 模型已切换为【MiniMax M2.5 (云端)】
- 此切换仅在当前会话中生效
- 关闭对话后将恢复为默认模型
- 您的配置和记忆不受影响
- session-memory hook 已开启（云端模型）
```

## 关键规则

1. **必须展示列表**：当用户说"切换模型"时，必须先展示可用模型列表
2. **必须等待选择**：不能直接替用户选择，必须等用户明确回复编号或名称
3. **使用完整 ID**：切换时必须使用完整的模型 ID（如 `ollama/qwen3:30b`），不能使用简称
4. **临时切换**：模型切换仅在当前会话中有效
5. **自动调整 Hook**：
   - 切换到本地模型（`ollama/*`）时，必须调用 `gateway config.patch` 关闭 `session-memory` hook
   - 切换到云端模型时，必须调用 `gateway config.patch` 开启 `session-memory` hook

## 注意事项

- 本地模型需要 Ollama 服务运行
- 联网模型需要网络连接
- 切换模型后，当前对话上下文可能需要重新理解

## 常见错误修正

| 错误做法 | 正确做法 |
|----------|----------|
| 用户说"切换模型"后直接切换 | 必须先展示列表 |
| 使用简称如"qwen" | 使用完整 ID 如 `ollama/qwen3:30b` |
| 替用户做决定 | 等待用户明确选择 |
