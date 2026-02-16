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

## 操作流程

### 步骤 1：用户触发
用户说"切换模型"或类似话语。

### 步骤 2：展示列表（必须步骤）
**必须先展示可用模型列表**，不能直接切换：

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
**必须等待用户明确选择**后才能执行切换。

### 步骤 4：执行切换
使用 `session_status` 工具的 `model` 参数进行切换。

### 步骤 5：调整 Memory Hook（关键步骤）

**⚠️ 切换模型后必须立即执行 Hook 调整！**

#### 判断模型类型
- **本地模型**：ID 以 `ollama/` 开头
- **云端模型**：其他所有模型

#### 切换到本地模型时
1. 先将当前对话重要信息写入 memory 文件（使用 write 工具）
2. 然后修改配置文件关闭 Hook：

```bash
# 使用 exec 工具修改配置
cd ~/.openclaw && cat openclaw.json | python3 -c "
import json,sys
d = json.load(sys.stdin)
d['hooks']['internal']['entries']['session-memory']['enabled'] = False
with open('openclaw.json', 'w') as f:
    json.dump(d, f, indent=2)
print('Hook 已关闭')
"
```

#### 切换到云端模型时
1. 检查当前 Hook 状态
2. 如果是 false，则开启 Hook：

```bash
# 使用 exec 工具修改配置
cd ~/.openclaw && cat openclaw.json | python3 -c "
import json,sys
d = json.load(sys.stdin)
d['hooks']['internal']['entries']['session-memory']['enabled'] = True
with open('openclaw.json', 'w') as f:
    json.dump(d, f, indent=2)
print('Hook 已开启')
"
```

### 步骤 6：确认切换
告诉用户切换成功，包括 Hook 状态。

## 关键规则

1. **必须展示列表**：当用户说"切换模型"时，必须先展示可用模型列表
2. **必须等待选择**：不能直接替用户选择
3. **使用完整 ID**：切换时必须使用完整的模型 ID
4. **Hook 自动调整**：
   - 本地模型 → 关闭 Hook
   - 云端模型 → 开启 Hook（如果当前是关闭状态）

## 注意事项

- 本地模型需要 Ollama 服务运行
- 切换模型后，当前对话上下文可能需要重新理解
- Hook 配置是持久化的，必须手动调整
