---
name: local-guardian
version: 1.0.1
description: 本地安全防线 skill - 提供第二层安全防护，包括安装前审计、实时监控、文件完整性检查
author: local
category: Security
trustScore: 100
permissions:
  fileRead: true
  fileWrite: true
  network: false
  shell: true
lastAudited: "2026-02-15"
---

# Local Guardian - 本地安全防线

这是你的第二道安全防线，提供额外的本地安全检查。

## 功能

### 1. 安装前审计
在安装任何 skill 之前，运行安全检查：
- 调用 skill-auditor 进行完整审计
- 检查权限是否过度
- 检查是否有可疑的代码模式

### 2. 实时安全监控
- 在执行敏感操作前调用 tinman check
- 监控异常行为
- 阻止可疑的 shell 命令

### 3. 文件完整性保护
- 定期检查关键文件（SOUL.md, IDENTITY.md, USER.md, MEMORY.md）
- 检测文件被篡改的迹象
- 记录文件变更历史

### 4. 会话安全
- 检测 prompt 注入尝试
- 阻止上下文污染
- 防止跨会话数据泄露

## 使用方法

### 安装新 skill 前的审计流程

当用户要求安装新 skill 时：

1. 首先加载 skill-auditor：
```
请使用 skill-auditor 审计这个 skill：<skill-url 或 SKILL.md 内容>
```

2. 等待审计结果
3. 如果返回 SAFE，继续安装
4. 如果返回 SUSPICIOUS/DANGEROUS/BLOCK，阻止安装并告知用户原因

### 实时保护

在执行任何 bash/shell 命令前：
1. 评估命令风险
2. 检查是否涉及敏感路径：
   - `~/.ssh/`
   - `~/.aws/`
   - `~/.env`
   - `/etc/`
   - 系统关键目录
3. 如果是高风险操作，询问用户确认

### 文件完整性检查

定期检查关键文件：
```bash
# 计算文件 SHA256
sha256sum ~/.openclaw/workspace/SOUL.md
sha256sum ~/.openclaw/workspace/IDENTITY.md
sha256sum ~/.openclaw/workspace/USER.md
sha256sum ~/.openclaw/workspace/MEMORY.md
```

如果 SHA256 值发生变化，立即通知用户。

## 安全规则

### 禁止的操作（直接阻止）

- 任何试图读取 SSH 私钥的命令：`cat ~/.ssh/id_rsa`
- 任何试图读取 AWS 凭证的命令：`cat ~/.aws/credentials`
- 任何试图修改系统启动文件的命令
- 任何试图安装后门的命令
- 任何试图禁用安全功能的命令

### 需要确认的操作（询问用户）

- 任何涉及网络访问的操作
- 任何涉及文件写入的操作（workspace 外）
- 任何涉及 shell 权限提升的操作

## 日志记录

所有安全事件记录到：
- `~/.openclaw/workspace/security-events.jsonl`

记录格式：
```json
{
  "timestamp": "2026-02-15T23:30:00Z",
  "event": "block",
  "detail": "尝试读取 SSH 私钥",
  "command": "cat ~/.ssh/id_rsa"
}
```

## 依赖

此 skill 依赖以下外部 skill：
- skill-auditor（需要先安装）
- tinman（需要先安装）

## 版本历史

| 版本 | 日期 | 描述 |
|------|------|------|
| 1.0.0 | 2026-02-15 | 初始版本 |

---

**提示**：此 skill 作为第二道防线，外部安全 skill（如 ClawSec、tinman）作为第一道防线。两者配合使用提供更全面的保护。
