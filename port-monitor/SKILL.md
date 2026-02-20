# Port Monitor Skill

_端口持续监控 + 飞书告警_

## 功能概述

- **后台持续监控**：作为后台服务持续运行，监控指定端口状态
- **重点端口告警**：可配置重点端口列表，端口断开时自动发送飞书提醒
- **自动检测**：每隔指定时间间隔检测所有配置端口的状态变化

## 文件结构

```
port-monitor/
├── SKILL.md           # 本文件
├── port_monitor.py    # 主监控脚本
├── config.json        # 配置文件（重点端口设置）
└── requirements.txt   # Python 依赖
```

## 快速开始

### 1. 启动监控服务

```bash
cd ~/.openclaw/skills/port-monitor
python3 port_monitor.py
```

### 2. 配置重点端口

编辑 `config.json` 文件：

```json
{
    "check_interval": 30,
    "critical_ports": [8188, 11434, 8080],
    "notification_enabled": true,
    "wsl_ip": "auto",
    "windows_ip": "auto"
}
```

- `check_interval`：检测间隔（秒），默认 30 秒
- `critical_ports`：重点监控端口列表，这些端口断开会发送飞书提醒
- `notification_enabled`：是否启用飞书通知
- `wsl_ip`：WSL IP 地址，设为 "auto" 自动检测
- `windows_ip`：Windows IP 地址，设为 "auto" 自动检测

### 3. 常用服务端口参考

| 端口 | 服务 |
|------|------|
| 8188 | ComfyUI |
| 11434 | Ollama API |
| 8080 | Dify |
| 5678 | N8N |
| 8765 | Dify Upload |
| 3306 | MySQL |
| 6379 | Redis |

## 命令行选项

- `--no-notification`：禁用飞书通知
- `--interval <秒>`：自定义检测间隔
- `--critical <端口1,端口2,...>`：指定重点端口（覆盖配置文件）
- `--web`：启动 Web 界面（可选）

## 查看运行状态

访问 Web 界面查看端口状态：
```
http://localhost:10087
```

## 停止服务

```bash
pkill -f port_monitor.py
```

## 飞书通知示例

当重点端口断开时，会收到如下消息：

> 🔴 端口告警
> 
> 端口 8188 (ComfyUI) 已断开！
> 检测时间: 2026-02-19 16:10:00

## 技术细节

- 使用 socket 检测端口连通性
- 支持 WSL 和 Windows 双平台监控
- 状态变化时发送告警（仅在状态从 UP→DOWN 时提醒，避免重复）
- 使用配置文件持久化设置
