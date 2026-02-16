# Hook 自检 Skill

_在每次新对话开始时自动检查并调整 Hook 状态_

## 概述

本 Skill 用于在新对话开始时自动检查并调整 session-memory hook 状态，确保：
- ☁️ 云端模型 → hook 开启
- 🖥️ 本地模型 → hook 关闭

## 触发条件

**自动触发**：每次新对话开始时（Session 初始化时）

## 检查逻辑

### 1. 获取当前模型
通过 `session_status` 或检查配置获取当前使用的模型

### 2. 判断模型类型
- **本地模型**：模型 ID 以 `ollama/` 开头
- **云端模型**：所有其他模型

### 3. 获取当前 Hook 状态
通过 `gateway config.get` 获取 `hooks.internal.entries.session-memory.enabled`

### 4. 执行调整

| 当前模型 | Hook 状态 | 需要操作 |
|----------|-----------|---------|
| 云端 | false | 开启 hook |
| 云端 | true | 不做修改 |
| 本地 | true | 关闭 hook |
| 本地 | false | 不做修改 |

## 执行命令

### 获取当前模型
```bash
# 方式1：通过 session_status
session_status

# 方式2：通过配置文件
cat ~/.openclaw/openclaw.json | jq '.agents.defaults.model.primary'
```

### 获取 Hook 状态
```bash
cat ~/.openclaw/openclaw.json | jq '.hooks.internal.entries.session-memory.enabled'
```

### 开启 Hook（云端模型）
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
  "note": "自检：云端模型已开启 session-memory hook"
}
```

### 关闭 Hook（本地模型）
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
  "note": "自检：本地模型已关闭 session-memory hook"
}
```

## 注意事项

1. **新对话时自检**：每次新 Session 开始时都应该执行这个检查
2. **模型切换时自检**：在 model-switcher Skill 中也应该调用这个逻辑
3. **配置持久化**：Hook 状态是持久化的，不会自动重置，所以必须手动调整
